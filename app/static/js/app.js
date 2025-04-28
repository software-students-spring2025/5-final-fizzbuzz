// Global variables for charts
let monthlyChart;
let categoryChart;

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    // Set up event listeners
    document.getElementById('transactionForm').addEventListener('submit', handleTransactionSubmit);
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);

    // Initialize charts
    initializeCharts();
    
    // Load initial data
    loadTransactions();
});

// Handle transaction form submission
async function handleTransactionSubmit(event) {
    event.preventDefault();
    
    const transaction = {
        amount: parseFloat(document.getElementById('amount').value),
        category: document.getElementById('category').value,
        description: document.getElementById('description').value,
        type: document.getElementById('type').value,
        user_id: sessionStorage.getItem('user_id')
    };

    try {
        const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(transaction)
        });

        if (!response.ok) {
            throw new Error('Failed to add transaction');
        }

        // Reset form and reload data
        event.target.reset();
        await loadTransactions();
        showAlert('Transaction added successfully!', 'success');
    } catch (error) {
        showAlert(error.message, 'danger');
    }
}

// Load transactions from the server
async function loadTransactions() {
    try {
        const response = await fetch(`/api/transactions/user/${sessionStorage.getItem('user_id')}`);
        if (!response.ok) {
            throw new Error('Failed to load transactions');
        }

        const transactions = await response.json();
        displayTransactions(transactions);
        updateCharts(transactions);
    } catch (error) {
        showAlert(error.message, 'danger');
    }
}

// Display transactions in the table
function displayTransactions(transactions) {
    const tbody = document.getElementById('transactionsList');
    tbody.innerHTML = '';

    transactions.forEach(transaction => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(transaction.date).toLocaleDateString()}</td>
            <td>${transaction.category}</td>
            <td>${transaction.description}</td>
            <td class="${transaction.type === 'income' ? 'text-success' : 'text-danger'}">
                ${transaction.type === 'income' ? '+' : '-'}$${Math.abs(transaction.amount).toFixed(2)}
            </td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteTransaction('${transaction._id}')">
                    Delete
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Initialize charts
function initializeCharts() {
    const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');

    monthlyChart = new Chart(monthlyCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Expenses',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }, {
                label: 'Income',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    categoryChart = new Chart(categoryCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40',
                    '#FF6384'
                ]
            }]
        },
        options: {
            responsive: true
        }
    });
}

// Update charts with transaction data
function updateCharts(transactions) {
    // Process data for monthly chart
    const monthlyData = processMonthlyData(transactions);
    monthlyChart.data.labels = monthlyData.labels;
    monthlyChart.data.datasets[0].data = monthlyData.expenses;
    monthlyChart.data.datasets[1].data = monthlyData.income;
    monthlyChart.update();

    // Process data for category chart
    const categoryData = processCategoryData(transactions);
    categoryChart.data.labels = categoryData.labels;
    categoryChart.data.datasets[0].data = categoryData.values;
    categoryChart.update();
}

// Process transaction data for monthly chart
function processMonthlyData(transactions) {
    const months = {};
    const labels = [];
    const expenses = [];
    const income = [];

    transactions.forEach(transaction => {
        const date = new Date(transaction.date);
        const monthYear = date.toLocaleString('default', { month: 'short', year: 'numeric' });
        
        if (!months[monthYear]) {
            months[monthYear] = { expenses: 0, income: 0 };
            labels.push(monthYear);
        }

        if (transaction.type === 'expense') {
            months[monthYear].expenses += transaction.amount;
        } else {
            months[monthYear].income += transaction.amount;
        }
    });

    labels.forEach(month => {
        expenses.push(months[month].expenses);
        income.push(months[month].income);
    });

    return { labels, expenses, income };
}

// Process transaction data for category chart
function processCategoryData(transactions) {
    const categories = {};
    
    transactions.forEach(transaction => {
        if (transaction.type === 'expense') {
            if (!categories[transaction.category]) {
                categories[transaction.category] = 0;
            }
            categories[transaction.category] += transaction.amount;
        }
    });

    return {
        labels: Object.keys(categories),
        values: Object.values(categories)
    };
}

// Delete a transaction
async function deleteTransaction(transactionId) {
    try {
        const response = await fetch(`/api/transactions/${transactionId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete transaction');
        }

        await loadTransactions();
        showAlert('Transaction deleted successfully!', 'success');
    } catch (error) {
        showAlert(error.message, 'danger');
    }
}

// Handle logout
function handleLogout() {
    sessionStorage.removeItem('user_id');
    window.location.href = '/login';
}

// Show alert message
function showAlert(message, type) {
    const alertElement = document.getElementById('errorAlert');
    alertElement.textContent = message;
    alertElement.className = `alert alert-${type}`;
    alertElement.classList.remove('d-none');

    setTimeout(() => {
        alertElement.classList.add('d-none');
    }, 3000);
} 