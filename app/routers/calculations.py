from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from math import pi, sqrt, sin, cos, tan, radians, degrees
import numpy as np
import json
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
from typing import Optional, Dict

# Предполагается, что 'templates' определен в app/utils.py
# from app.utils import templates
# Для автономности определим здесь:
templates = Jinja2Templates(directory="app/templates")


router = APIRouter(prefix="/calculations", tags=["calculations"])

@router.get("/")
async def calculations_main(request: Request):
    return templates.TemplateResponse("calculations/calculations.html", {"request": request})

DIODES = [
    {"name": "2Д201А", "Uobr": 100, "Imax": 5, "U_op": 1},
    {"name": "2Д201Б", "Uobr": 100, "Imax": 10, "U_op": 1},
    {"name": "2Д201В", "Uobr": 200, "Imax": 5, "U_op": 1},
    {"name": "2Д201Г", "Uobr": 200, "Imax": 10, "U_op": 1},
    {"name": "КД202А", "Uobr": 50, "Imax": 5, "U_op": 0.9},
    {"name": "КД202Б", "Uobr": 50, "Imax": 3.5, "U_op": 0.9},
    {"name": "КД202В", "Uobr": 100, "Imax": 5, "U_op": 0.9},
    {"name": "КД202Г", "Uobr": 100, "Imax": 3.5, "U_op": 0.9},
    {"name": "КД202Д", "Uobr": 200, "Imax": 5, "U_op": 0.9},
    {"name": "КД202Е", "Uobr": 200, "Imax": 3.5, "U_op": 0.9},
    {"name": "КД202Ж", "Uobr": 300, "Imax": 5, "U_op": 0.9},
    {"name": "КД202И", "Uobr": 300, "Imax": 3.5, "U_op": 0.9},
    {"name": "КД202К", "Uobr": 400, "Imax": 5, "U_op": 0.9},
    {"name": "КД203A", "Uobr": 600, "Imax": 10, "U_op": 1},
    {"name": "КД206A", "Uobr": 400, "Imax": 10, "U_op": 1.2},
]

class RectifierCalculator:
    def __init__(self, schema: str, U0: float, I0: float, kp: float):
        self.schema = schema
        self.U0 = U0
        self.I0 = I0
        self.kp = kp
        self.m = 1
        self.r_transformer = 0.0
        self.r_diode = 0.0
        self.validate_input()

    def validate_input(self):
        if self.U0 <= 0 or self.I0 <= 0 or self.kp <= 0:
            raise ValueError("Все значения должны быть положительными")
        if self.schema not in ['а', 'б', 'в']:
            raise ValueError("Некорректный тип схемы. Допустимые значения: 'а', 'б', 'в'")

    @staticmethod
    def select_diode(Ud: float, Id: float) -> Optional[Dict]:
        suitable = []
        for diode in DIODES:
            if diode["Uobr"] >= Ud and diode["Imax"] >= Id:
                # Рассчитываем запас прочности
                safety_margin_u = (diode["Uobr"] - Ud) / Ud if Ud > 0 else float('inf')
                safety_margin_i = (diode["Imax"] - Id) / Id if Id > 0 else float('inf')
                # Используем сумму запасов как критерий выбора, минимизируя ее
                total_safety = safety_margin_u + safety_margin_i
                suitable.append({**diode, "safety": round(total_safety * 100, 2)})
        
        if not suitable:
            return None
        # Выбираем диод с минимальным запасом прочности (самый близкий по параметрам)
        return min(suitable, key=lambda x: x["safety"])

    def _calculate_resistance(self, Rn: float) -> float:
        P0 = self.U0 * self.I0
        self.r_transformer = 0.1 * Rn if P0 < 10 else 0.07 * Rn
        diodes_count = 2 if self.schema == 'в' else 1
        # Используем более реалистичный подход к сопротивлению диода
        self.r_diode = DIODES[0]["U_op"] / (self.I0 / self.m) if self.I0 > 0 else 0
        return self.r_transformer + diodes_count * self.r_diode

    def _calculate_theta(self, Rn: float) -> float:
        r = self._calculate_resistance(Rn)
        A = (self.I0 / self.U0) * (r / self.m) * pi
        
        # Используем метод Ньютона для решения уравнения tan(theta) - theta = A
        theta = pi / 4  # Начальное приближение
        for _ in range(100): # 100 итераций для сходимости
            f = tan(theta) - theta - A
            df = (1 / cos(theta))**2 - 1
            if abs(df) < 1e-9: # Избегаем деления на ноль
                break
            delta = f / df
            theta -= delta
            if abs(delta) < 1e-6: # Условие сходимости
                break
        return max(0, min(pi/2 - 0.01, theta)) # Ограничиваем угол

    def _calculate_transformer_currents(self, theta: float) -> tuple:
        # Формула для I2
        numerator = pi * (theta * (1 + 0.5 * cos(2 * theta)) - 0.75 * sin(2 * theta))
        denominator = sin(theta) - theta * cos(theta)
        
        if abs(denominator) < 1e-9:
            I2 = 0
        else:
            I2 = (self.I0 / self.m) * sqrt(max(0, numerator)) / denominator

        U2m = self.U0 / cos(theta)
        U2 = U2m / sqrt(2)
        n_tr = U2 / 220 # Напряжение сети 220В

        if self.schema == "а":
            I1 = n_tr * sqrt(max(0, I2**2 - self.I0**2))
        else:
            I1 = n_tr * I2
        
        return I1, I2

    def generate_plot(self, theta: float) -> str:
        theta_rad = theta
        theta_deg = degrees(theta_rad)
        
        # Данные для кривой
        theta_vals = np.linspace(0.01, np.pi/2 - 0.01, 400)
        A_vals = np.tan(theta_vals) - theta_vals
        theta_degrees_vals = np.degrees(theta_vals)
        
        # Точка на графике
        A_point = np.tan(theta_rad) - theta_rad
        
        # Создание интерактивного графика с помощью Plotly
        fig = go.Figure()

        # Добавляем основную линию графика
        fig.add_trace(go.Scatter(
            x=A_vals, 
            y=theta_degrees_vals, 
            mode='lines', 
            name=r'$\theta = f(A)$',
            line=dict(color='royalblue', width=3)
        ))

        # Добавляем маркер для вычисленной точки
        fig.add_trace(go.Scatter(
            x=[A_point], 
            y=[theta_deg], 
            mode='markers', 
            name=f'Ваша точка: θ = {theta_deg:.1f}°',
            marker=dict(color='crimson', size=12, symbol='star', line=dict(width=2, color='white'))
        ))

        # Обновляем макет графика
        fig.update_layout(
            title=dict(text="<b>Зависимость угла отсечки θ от параметра A</b>", font=dict(size=20), x=0.5),
            xaxis_title="<b>Параметр A = tg(θ) - θ</b>",
            yaxis_title="<b>Угол отсечки θ (градусы)</b>",
            xaxis=dict(range=[0, max(1, A_point * 1.5)], gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(range=[0, 90], gridcolor='rgba(255,255,255,0.1)'),
            template="plotly_dark",
            legend=dict(y=0.01, x=0.01, bgcolor='rgba(0,0,0,0.5)', bordercolor='rgba(255,255,255,0.2)'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )

        # Преобразуем график в JSON
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def calculate_parameters(self) -> Dict:
        scheme_params = {
            'а': {'U_obr': 3*self.U0, 'I_sr': self.I0, 'm': 1},
            'б': {'U_obr': 3*self.U0, 'I_sr': 0.5*self.I0, 'm': 2},
            'в': {'U_obr': 1.5*self.U0, 'I_sr': 0.5*self.I0, 'm': 2}
        }[self.schema]
        
        self.m = scheme_params['m']
        diode = self.select_diode(scheme_params['U_obr'], scheme_params['I_sr'])
        
        if not diode:
            raise ValueError("Не найден подходящий диод по предварительным расчетам")

        Rn = self.U0 / self.I0
        theta = self._calculate_theta(Rn)
        I1, I2 = self._calculate_transformer_currents(theta)
        U2m = self.U0 / cos(theta)
        U2 = U2m / sqrt(2)
        n_tr = U2 / 220
        r = self._calculate_resistance(Rn)
        A = (self.I0 / self.U0) * (r / self.m) * pi
        C = (pi - self.m * theta) / (self.m * (2 * pi * 50) * self.kp * Rn)

        Idmax = (U2m - self.U0) / r if r > 0 else float('inf')
        
        Uobr_calc = 2 * U2m if self.schema == 'б' else U2m

        final_diode = self.select_diode(Uobr_calc, Idmax)
        if not final_diode:
             final_diode = diode # Если по точным расчетам не нашли, оставляем первый

        return {
            'diode': final_diode,
            'Rn': round(Rn, 3),
            'P_н': round(self.U0 * self.I0, 3),
            'I1': round(I1, 3),
            'I2': round(I2, 3),
            'theta_deg': round(degrees(theta), 1),
            'U2m': round(U2m, 3),
            'U2': round(U2, 3),
            'k': round(n_tr, 4),
            'r_tr': round(self.r_transformer, 3),
            'r_pr': round(self.r_diode, 3),
            'r': round(r, 3),
            'A': round(A, 3),
            'plot_json': self.generate_plot(theta),
            'C': round(C * 1e6, 2), # в мкФ
            'U0': self.U0,
            'I0': self.I0,
            'm': self.m,
            'kp': self.kp,
            'Idmax': round(Idmax, 3),
            'Uobr_calc': round(Uobr_calc, 3),
            'schema': self.schema,
        }

@router.get("/rectifier")
async def show_rectifier_form(request: Request):
    return templates.TemplateResponse("calculations/calculations_rectifier.html", {"request": request})

@router.post("/rectifier")
async def calculate_rectifier(
    request: Request,
    schema: str = Form(...),
    U0: float = Form(...),
    I0: float = Form(...),
    kp: float = Form(...)
):
    try:
        calculator = RectifierCalculator(schema.lower(), U0, I0, kp)
        result = calculator.calculate_parameters()
    except (ValueError, ZeroDivisionError) as e:
        return templates.TemplateResponse("calculations/calculations_rectifier.html", {
            "request": request,
            "error": str(e),
            "U0": U0,
            "I0": I0,
            "kp": kp,
            "schema": schema
        })
    
    return templates.TemplateResponse("calculations/calculations_rectifier.html", {
        "request": request,
        "result": result,
        "U0": U0,
        "I0": I0,
        "kp": kp,
        "schema": schema
    })
