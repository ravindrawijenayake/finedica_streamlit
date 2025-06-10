document.getElementById('budgetForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const form = new FormData(this);
  
    // Income
    const incomeKeys = ['salary', 'dividends', 'statePension', 'pension', 'benefits', 'otherIncome'];
    let totalIncome = incomeKeys.reduce((sum, key) => sum + parseFloat(form.get(key) || 0), 0);
  
    // Home
    const homeKeys = ['gas', 'electric', 'water', 'councilTax', 'phone', 'internet', 'mobilePhone', 'food', 'otherHome'];
    let totalHome = homeKeys.reduce((sum, key) => sum + parseFloat(form.get(key) || 0), 0);
  
    // Travel
    const travelKeys = ['petrol', 'carTax', 'carInsurance', 'maintenance', 'publicTransport', 'otherTravel'];
    let totalTravel = travelKeys.reduce((sum, key) => sum + parseFloat(form.get(key) || 0), 0);
  
    // For now, set others to zero (to be implemented)
    let totalMisc = 0;
    let totalChildren = 0;
    let totalInsurance = 0;
    let totalPayslip = 0;
    let totalExpenses = totalHome + totalTravel + totalMisc + totalChildren + totalInsurance + totalPayslip;
  
    let surplus = totalIncome - totalExpenses;
  
    // Percentages
    let percent = val => ((val / totalIncome) * 100).toFixed(2);
    let resultsHTML = `
      <h2>Results</h2>
      <p>Total Income: £${totalIncome.toFixed(2)}</p>
      <p>Total Expenses: £${totalExpenses.toFixed(2)}</p>
      <p>Surplus: £${surplus.toFixed(2)} (${percent(surplus)}%)</p>
      <p>Home: £${totalHome.toFixed(2)} (${percent(totalHome)}%)</p>
      <p>Travel: £${totalTravel.toFixed(2)} (${percent(totalTravel)}%)</p>
    `;
  
    document.getElementById('results').innerHTML = resultsHTML;
  
    const ctx = document.getElementById('expenseChart').getContext('2d');
    new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['Surplus', 'Home', 'Travel'],
        datasets: [{
          data: [surplus, totalHome, totalTravel],
          backgroundColor: ['#4caf50', '#2196f3', '#ff9800']
        }]
      },
      options: {
        responsive: true
      }
    });
  });
  
  