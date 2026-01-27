/**
 * Quantum Portfolio Optimizer - Frontend Application
 * 
 * Handles:
 * - Stock fetching and selection
 * - Configuration management
 * - API communication
 * - Results display
 */

// Configuration
const CONFIG = {
    // API URL - change this for production
    API_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : 'https://quantum-portfolio-api.onrender.com',

    // Default values
    DEFAULT_K: 3,
    DEFAULT_LAMBDA: 0.5,
    DEFAULT_P: 1,
    DEFAULT_ITERATIONS: 50,
    DEFAULT_SHOTS: 1024
};

// State management
const state = {
    stocks: [],
    selectedStocks: new Set(),
    portfolioSize: CONFIG.DEFAULT_K,
    riskAversion: CONFIG.DEFAULT_LAMBDA,
    isLoading: false,
    results: null
};

// DOM Elements
const elements = {
    stockGrid: document.getElementById('stockGrid'),
    selectedCount: document.getElementById('selectedCount'),
    selectAllBtn: document.getElementById('selectAllBtn'),
    clearAllBtn: document.getElementById('clearAllBtn'),
    portfolioSize: document.getElementById('portfolioSize'),
    riskAversion: document.getElementById('riskAversion'),
    riskValue: document.getElementById('riskValue'),
    qaoaDepth: document.getElementById('qaoaDepth'),
    maxIterations: document.getElementById('maxIterations'),
    shots: document.getElementById('shots'),
    optimizeBtn: document.getElementById('optimizeBtn'),
    resultsPanel: document.getElementById('resultsPanel'),
    errorToast: document.getElementById('errorToast'),
    errorMessage: document.getElementById('errorMessage')
};

/**
 * Initialize the application
 */
async function init() {
    console.log('🚀 Initializing Quantum Portfolio Optimizer...');

    // Set up event listeners
    setupEventListeners();

    // Load stocks
    await loadStocks();

    console.log('✅ Application initialized');
}

/**
 * Set up all event listeners
 */
function setupEventListeners() {
    // Portfolio size buttons
    document.querySelectorAll('.size-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.portfolioSize = parseInt(btn.dataset.value);
            elements.portfolioSize.value = state.portfolioSize;
        });
    });

    // Risk aversion slider
    elements.riskAversion.addEventListener('input', () => {
        const value = elements.riskAversion.value / 100;
        state.riskAversion = value;
        elements.riskValue.textContent = value.toFixed(2);
    });

    // Select/Clear all buttons
    elements.selectAllBtn.addEventListener('click', selectAllStocks);
    elements.clearAllBtn.addEventListener('click', clearAllStocks);
    elements.optimizeBtn.addEventListener('click', optimizePortfolio);
}

/**
 * Load available stocks from API
 */
async function loadStocks() {
    try {
        showStockLoading();

        const response = await fetch(`${CONFIG.API_URL}/api/stocks`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        state.stocks = data.stocks;

        renderStockGrid();
        console.log(`📈 Loaded ${state.stocks.length} stocks`);

    } catch (error) {
        console.error('Failed to load stocks:', error);
        showError('Failed to load stocks. Using demo data...');

        // Use demo data as fallback
        state.stocks = getDemoStocks();
        renderStockGrid();
    }
}

/**
 * Render the stock selection grid
 */
function renderStockGrid() {
    elements.stockGrid.innerHTML = state.stocks.map(stock => `
        <div class="stock-card" data-ticker="${stock.ticker}" onclick="toggleStock('${stock.ticker}')">
            <div class="stock-card-content">
                <div class="stock-ticker">
                    <span>${stock.ticker}</span>
                    <div class="stock-checkbox"></div>
                </div>
                <div class="stock-name">${stock.name}</div>
                <div class="stock-sector">${stock.sector}</div>
            </div>
        </div>
    `).join('');

    updateSelectedCount();
}

/**
 * Toggle stock selection
 */
function toggleStock(ticker) {
    const card = document.querySelector(`[data-ticker="${ticker}"]`);

    if (state.selectedStocks.has(ticker)) {
        state.selectedStocks.delete(ticker);
        card.classList.remove('selected');
    } else {
        state.selectedStocks.add(ticker);
        card.classList.add('selected');
    }

    updateSelectedCount();
}

/**
 * Select all stocks
 */
function selectAllStocks() {
    state.stocks.forEach(stock => {
        state.selectedStocks.add(stock.ticker);
    });

    document.querySelectorAll('.stock-card').forEach(card => {
        card.classList.add('selected');
    });

    updateSelectedCount();
}

/**
 * Clear all selections
 */
function clearAllStocks() {
    state.selectedStocks.clear();

    document.querySelectorAll('.stock-card').forEach(card => {
        card.classList.remove('selected');
    });

    updateSelectedCount();
}

/**
 * Update selected count display
 */
function updateSelectedCount() {
    const count = state.selectedStocks.size;
    elements.selectedCount.textContent = `${count} selected`;
}

async function searchStocks(query) {
    if (!query || query.trim().length < 1) {
        elements.searchResults.style.display = 'none';
        return;
    }

    try {
        const response = await fetch(`${CONFIG.API_URL}/api/stocks/search?query=${encodeURIComponent(query)}&limit=10`);
        const data = await response.json();

        if (data.stocks.length === 0) {
            elements.searchResults.innerHTML = '<div class="search-no-results">No stocks found</div>';
        } else {
            elements.searchResults.innerHTML = data.stocks.map(stock => `
                <div class="search-result-item" onclick="addStockToSelection('${stock.ticker}')">
                    <div class="search-result-ticker">${stock.ticker}</div>
                    <div class="search-result-name">${stock.name}</div>
                    <div class="search-result-sector">${stock.sector}</div>
                </div>
            `).join('');
        }
        elements.searchResults.style.display = 'block';
    } catch (error) {
        console.error('Search error:', error);
    }
}

function addStockToSelection(ticker) {
    const stockEntry = state.stocks.find(s => s.ticker === ticker);
    if (!stockEntry) {
        state.stocks.push({
            ticker: ticker,
            name: 'Loading...',
            sector: 'Unknown',
            symbol: `${ticker}.NS`
        });
    }

    const card = document.querySelector(`[data-ticker="${ticker}"]`);
    if (!card) {
        renderStockGrid();
    }

    state.selectedStocks.add(ticker);
    const newCard = document.querySelector(`[data-ticker="${ticker}"]`);
    if (newCard) {
        newCard.classList.add('selected');
        newCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    updateSelectedCount();
    elements.stockSearch.value = '';
    elements.searchResults.style.display = 'none';
}

/**
 * Run portfolio optimization
 */
async function optimizePortfolio() {
    // Validate selection
    if (state.selectedStocks.size < 3) {
        showError('Please select at least 3 stocks');
        return;
    }

    if (state.portfolioSize > state.selectedStocks.size) {
        showError(`Portfolio size (${state.portfolioSize}) cannot exceed selected stocks (${state.selectedStocks.size})`);
        return;
    }

    // Show loading state
    setLoadingState(true);

    try {
        const requestBody = {
            stocks: Array.from(state.selectedStocks),
            k: state.portfolioSize,
            lambda_param: state.riskAversion,
            p: parseInt(elements.qaoaDepth.value),
            maxiter: parseInt(elements.maxIterations.value),
            shots: parseInt(elements.shots.value)
        };

        console.log('🔄 Starting optimization...', requestBody);

        const response = await fetch(`${CONFIG.API_URL}/api/optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Optimization failed');
        }

        const result = await response.json();
        console.log('✅ Optimization complete:', result);

        state.results = result;
        displayResults(result);

    } catch (error) {
        console.error('Optimization error:', error);
        showError(`Optimization failed: ${error.message}`);
    } finally {
        setLoadingState(false);
    }
}

/**
 * Display optimization results
 */
function displayResults(result) {
    // Show results panel
    elements.resultsPanel.style.display = 'block';

    // Scroll to results
    elements.resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Update metrics
    document.getElementById('resultReturn').textContent =
        `${(result.portfolio.expected_return * 100).toFixed(2)}%`;
    document.getElementById('resultRisk').textContent =
        `${(result.portfolio.portfolio_risk * 100).toFixed(2)}%`;
    document.getElementById('resultSharpe').textContent =
        result.portfolio.sharpe_ratio.toFixed(3);

    // Computation time
    document.getElementById('computationTime').textContent =
        `⏱️ ${result.computation_time.toFixed(2)}s`;

    // Selected stocks
    const selectedGrid = document.getElementById('selectedStocksGrid');
    selectedGrid.innerHTML = result.portfolio.selected_stocks.map((stock, i) => `
        <div class="selected-stock-chip">
            <span>${stock}</span>
            <span class="chip-weight">${(result.portfolio.weights[i] * 100).toFixed(1)}%</span>
        </div>
    `).join('');

    // QAOA metrics
    document.getElementById('metricQubits').textContent = result.qaoa_metrics.num_qubits;
    document.getElementById('metricDepth').textContent = result.qaoa_metrics.circuit_depth;
    document.getElementById('metricLayers').textContent = result.qaoa_metrics.qaoa_layers;
    document.getElementById('metricIterations').textContent = result.qaoa_metrics.iterations;

    // Stock metrics table
    const tableBody = document.querySelector('#stockMetricsTable tbody');
    tableBody.innerHTML = Object.entries(result.stock_metrics)
        .map(([ticker, metrics]) => `
            <tr>
                <td>${ticker}</td>
                <td>${(metrics.expected_return * 100).toFixed(2)}%</td>
                <td>${(metrics.volatility * 100).toFixed(2)}%</td>
                <td class="${metrics.selected ? 'status-selected' : 'status-not-selected'}">
                    ${metrics.selected ? '✓ Selected' : '—'}
                </td>
            </tr>
        `).join('');
}

/**
 * Set loading state
 */
function setLoadingState(loading) {
    state.isLoading = loading;

    const btnText = elements.optimizeBtn.querySelector('.btn-text');
    const btnLoading = elements.optimizeBtn.querySelector('.btn-loading');
    const btnIcon = elements.optimizeBtn.querySelector('.btn-icon');

    if (loading) {
        btnText.style.display = 'none';
        btnIcon.style.display = 'none';
        btnLoading.style.display = 'flex';
        elements.optimizeBtn.disabled = true;
    } else {
        btnText.style.display = 'inline';
        btnIcon.style.display = 'inline';
        btnLoading.style.display = 'none';
        elements.optimizeBtn.disabled = false;
    }
}

/**
 * Show loading placeholder in stock grid
 */
function showStockLoading() {
    elements.stockGrid.innerHTML = `
        <div class="loading-placeholder">
            <div class="spinner"></div>
            <p>Loading stocks...</p>
        </div>
    `;
}

/**
 * Show error message
 */
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorToast.style.display = 'flex';

    // Auto-hide after 5 seconds
    setTimeout(hideError, 5000);
}

/**
 * Hide error message
 */
function hideError() {
    elements.errorToast.style.display = 'none';
}

// Make hideError available globally for the close button
window.hideError = hideError;

/**
 * Get demo stocks for fallback
 */
function getDemoStocks() {
    return [
        { ticker: 'RELIANCE', name: 'Reliance Industries', sector: 'Energy', symbol: 'RELIANCE.NS' },
        { ticker: 'TCS', name: 'Tata Consultancy Services', sector: 'IT', symbol: 'TCS.NS' },
        { ticker: 'INFY', name: 'Infosys', sector: 'IT', symbol: 'INFY.NS' },
        { ticker: 'HDFCBANK', name: 'HDFC Bank', sector: 'Banking', symbol: 'HDFCBANK.NS' },
        { ticker: 'ICICIBANK', name: 'ICICI Bank', sector: 'Banking', symbol: 'ICICIBANK.NS' },
        { ticker: 'HINDUNILVR', name: 'Hindustan Unilever', sector: 'FMCG', symbol: 'HINDUNILVR.NS' },
        { ticker: 'SBIN', name: 'State Bank of India', sector: 'Banking', symbol: 'SBIN.NS' },
        { ticker: 'BHARTIARTL', name: 'Bharti Airtel', sector: 'Telecom', symbol: 'BHARTIARTL.NS' },
        { ticker: 'KOTAKBANK', name: 'Kotak Mahindra Bank', sector: 'Banking', symbol: 'KOTAKBANK.NS' },
        { ticker: 'LT', name: 'Larsen & Toubro', sector: 'Infrastructure', symbol: 'LT.NS' }
    ];
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', init);
