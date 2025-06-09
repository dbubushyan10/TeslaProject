// document.getElementById("rectifierForm").addEventListener("submit", async function(event) {
//     event.preventDefault();

//     const schema = document.getElementById("schema").value;
//     const U0 = parseFloat(document.getElementById("U0").value);
//     const I0 = parseFloat(document.getElementById("I0").value);
//     const kp = parseFloat(document.getElementById("kp").value);

//     // Отправляем данные на сервер для расчёта
//     const response = await fetch("/calculations/rectifier", {
//         method: "POST",
//         body: new URLSearchParams({
//             U0: U0,
//             I0: I0,
//             kp: kp,
//             schema: schema
//         }),
//         headers: {
//             'Content-Type': 'application/x-www-form-urlencoded'
//         }
//     });

//     const result = await response.json();

//     if (result.success) {
//         displayResults(result.results);
//         drawGraph(result.results.theta);
//     } else {
//         alert("Произошла ошибка: " + result.error);
//     }
// });

// function displayResults(results) {
//     const resultsDiv = document.getElementById("results");
//     resultsDiv.innerHTML = `
//         <p>Диод: ${results.diode}</p>
//         <p>θ: ${results.theta}°</p>
//         <p>U_обр: ${results.U_obr} В</p>
//         <p>I_ср: ${results.I_op} А</p>
//         <p>I_m: ${results.I_m} А</p>
//         <p>R_н: ${results.Rn} Ом</p>
//         <p>P_н: ${results.P0} Вт</p>
//         <p>I2: ${results.I2} А</p>
//         <p>I1: ${results.I1} А</p>
//         <p>C: ${results.C} Ф</p>
//         <p>U_dp: ${results.U_dp} В</p>
//         <p>n_tr: ${results.n_tr}</p>
//         <p>U2: ${results.U2} В</p>
//     `;
// }

// function drawGraph(theta) {
//     const ctx = document.getElementById('thetaGraph').getContext('2d');
    
//     // Генерация данных для графика
//     const thetaValues = [];
//     const tgThetaMinusTheta = [];
//     for (let i = 0; i <= 100; i++) {
//         let angle = i * Math.PI / 100;
//         thetaValues.push(angle);
//         tgThetaMinusTheta.push(Math.tan(angle) - angle);
//     }

//     // Создание графика
//     new Chart(ctx, {
//         type: 'line',
//         data: {
//             labels: thetaValues.map(theta => theta.toFixed(3)),
//             datasets: [{
//                 label: 'tg(θ) - θ',
//                 data: tgThetaMinusTheta,
//                 borderColor: 'rgba(75, 192, 192, 1)',
//                 borderWidth: 2,
//                 fill: false
//             }]
//         },
//         options: {
//             responsive: true,
//             scales: {
//                 x: {
//                     ticks: {
//                         callback: function(value) {
//                             return (parseFloat(value) * 180 / Math.PI).toFixed(1) + "°";
//                         }
//                     }
//                 }
//             }
//         }
//     });
// }
