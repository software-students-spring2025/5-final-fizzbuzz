// Chart configurations
let monthlyChart = null;
let categoryChart = null;

// Initialize charts
function initCharts() {
    const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');

    monthlyChart = new Chart(monthlyCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Monthly Spending',
                data: [],
                borderColor: '#4a90e2',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    categoryChart = new Chart(categoryCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#4a90e2',
                    '#50e3c2',
                    '#f5a623',
                    '#d0021b',
                    '#9013fe'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Show error message to user
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('.container').insertBefore(errorDiv, document.querySelector('.row'));
}

// Check database connection
async function checkDatabaseConnection() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        if (data.database === 'disconnected') {
            showError('Database connection is not available. Some features may be limited.');
        }
    } catch (error) {
        console.error('Error checking database connection:', error);
        showError('Unable to connect to the server. Please try again later.');
    }
}

// Fetch and display transactions
async function fetchTransactions() {
    try {
        const response = await fetch('/api/transactions');
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to fetch transactions');
        }
        const transactions = await response.json();
        displayTransactions(transactions);
    } catch (error) {
        console.error('Error fetching transactions:', error);
        showError('Unable to fetch transactions. Please try again later.');
    }
}

// Display transactions in the table
function displayTransactions(transactions) {
    const tbody = document.querySelector('#transactionsTable tbody');
    tbody.innerHTML = '';

    if (transactions.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="5" class="text-center">No transactions found</td>';
        tbody.appendChild(row);
        return;
    }

    transactions.forEach(transaction => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(transaction.date).toLocaleDateString()}</td>
            <td>${transaction.category}</td>
            <td>${transaction.description}</td>
            <td>$${transaction.amount.toFixed(2)}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteTransaction('${transaction._id}')">
                    Delete
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Add new transaction
async function addTransaction(event) {
    event.preventDefault();

    const amount = parseFloat(document.getElementById('amount').value);
    const category = document.getElementById('category').value;
    const description = document.getElementById('description').value;

    try {
        const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                amount,
                category,
                description
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to add transaction');
        }

        document.getElementById('transactionForm').reset();
        await Promise.all([
            fetchTransactions(),
            updateCharts()
        ]);
    } catch (error) {
        console.error('Error adding transaction:', error);
        showError('Unable to add transaction. Please try again later.');
    }
}

// Delete transaction
async function deleteTransaction(id) {
    try {
        const response = await fetch(`/api/transactions/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to delete transaction');
        }

        await Promise.all([
            fetchTransactions(),
            updateCharts()
        ]);
    } catch (error) {
        console.error('Error deleting transaction:', error);
        showError('Unable to delete transaction. Please try again later.');
    }
}

// Update charts with latest data
async function updateCharts() {
    try {
        const [monthlyResponse, categoryResponse] = await Promise.all([
            fetch('/api/analytics/monthly'),
            fetch('/api/analytics/categories')
        ]);

        if (!monthlyResponse.ok || !categoryResponse.ok) {
            throw new Error('Failed to fetch analytics data');
        }

        const [monthlyData, categoryData] = await Promise.all([
            monthlyResponse.json(),
            categoryResponse.json()
        ]);

        // Update monthly chart
        monthlyChart.data.labels = monthlyData.map(d => 
            `${d._id.year}-${d._id.month.toString().padStart(2, '0')}`
        );
        monthlyChart.data.datasets[0].data = monthlyData.map(d => d.total);
        monthlyChart.update();

        // Update category chart
        categoryChart.data.labels = categoryData.map(d => d._id);
        categoryChart.data.datasets[0].data = categoryData.map(d => d.total);
        categoryChart.update();
    } catch (error) {
        console.error('Error updating charts:', error);
        showError('Unable to update analytics. Please try again later.');
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    checkDatabaseConnection();
    fetchTransactions();
    updateCharts();
});

document.getElementById('transactionForm').addEventListener('submit', addTransaction); 