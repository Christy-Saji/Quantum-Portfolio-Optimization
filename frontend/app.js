// Configuration
const CONFIG = {
    API_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : 'https://quantum-portfolio-api.onrender.com',
    DEFAULT_K: 3, DEFAULT_LAMBDA: 0.5, DEFAULT_P: 1,
    DEFAULT_ITERATIONS: 50, DEFAULT_SHOTS: 1024
};

// State
const state = {
    stocks: [], selectedStocks: new Set(),
    portfolioSize: CONFIG.DEFAULT_K, riskAversion: CONFIG.DEFAULT_LAMBDA,
    isLoading: false, results: null
};

// DOM refs
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
    errorMessage: document.getElementById('errorMessage'),
    sectorDiversify: document.getElementById('sectorDiversify'),
    sectorToggleLabel: document.getElementById('sectorToggleLabel'),
    sectorLimitGroup: document.getElementById('sectorLimitGroup'),
    maxPerSector: document.getElementById('maxPerSector')
};

async function init() {
    setupEventListeners();
    await loadStocks();
}

function setupEventListeners() {
    document.querySelectorAll('.size-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.portfolioSize = parseInt(btn.dataset.value);
            elements.portfolioSize.value = state.portfolioSize;
        });
    });

    elements.riskAversion.addEventListener('input', () => {
        const value = elements.riskAversion.value / 100;
        state.riskAversion = value;
        elements.riskValue.textContent = value.toFixed(2);
    });

    elements.sectorDiversify.addEventListener('change', () => {
        const enabled = elements.sectorDiversify.checked;
        elements.sectorToggleLabel.textContent = enabled ? 'Enabled' : 'Disabled';
        elements.sectorToggleLabel.style.color = enabled ? '#10b981' : '';
        elements.sectorLimitGroup.style.display = enabled ? 'block' : 'none';
    });

    elements.selectAllBtn.addEventListener('click', selectAllStocks);
    elements.clearAllBtn.addEventListener('click', clearAllStocks);
    elements.optimizeBtn.addEventListener('click', optimizePortfolio);
}

async function loadStocks() {
    try {
        showStockLoading();
        const response = await fetch(`${CONFIG.API_URL}/api/stocks`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        state.stocks = data.stocks;
        renderStockGrid();
    } catch (error) {
        console.error('Failed to load stocks:', error);
        showError('Failed to load stocks. Using demo data...');
        state.stocks = getDemoStocks();
        renderStockGrid();
    }
}

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

function selectAllStocks() {
    state.stocks.forEach(stock => state.selectedStocks.add(stock.ticker));
    document.querySelectorAll('.stock-card').forEach(card => card.classList.add('selected'));
    updateSelectedCount();
}

function clearAllStocks() {
    state.selectedStocks.clear();
    document.querySelectorAll('.stock-card').forEach(card => card.classList.remove('selected'));
    updateSelectedCount();
}

function updateSelectedCount() {
    elements.selectedCount.textContent = `${state.selectedStocks.size} selected`;
}

async function optimizePortfolio() {
    if (state.selectedStocks.size < 3) { showError('Please select at least 3 stocks'); return; }
    if (state.portfolioSize > state.selectedStocks.size) {
        showError(`Portfolio size (${state.portfolioSize}) cannot exceed selected stocks (${state.selectedStocks.size})`);
        return;
    }

    setLoadingState(true);
    try {
        const requestBody = {
            stocks: Array.from(state.selectedStocks),
            k: state.portfolioSize,
            lambda_param: state.riskAversion,
            p: parseInt(elements.qaoaDepth.value),
            maxiter: parseInt(elements.maxIterations.value),
            shots: parseInt(elements.shots.value),
            sector_diversify: elements.sectorDiversify.checked,
            max_per_sector: parseInt(elements.maxPerSector.value)
        };

        const response = await fetch(`${CONFIG.API_URL}/api/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Optimization failed');
        }

        const result = await response.json();
        state.results = result;
        displayResults(result);
    } catch (error) {
        console.error('Optimization error:', error);
        showError(`Optimization failed: ${error.message}`);
    } finally {
        setLoadingState(false);
    }
}

function displayResults(result) {
    elements.resultsPanel.style.display = 'block';
    elements.resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });

    document.getElementById('resultReturn').textContent = `${(result.portfolio.expected_return * 100).toFixed(2)}%`;
    document.getElementById('resultRisk').textContent = `${(result.portfolio.portfolio_risk * 100).toFixed(2)}%`;
    document.getElementById('resultSharpe').textContent = result.portfolio.sharpe_ratio.toFixed(3);
    document.getElementById('computationTime').textContent = `⏱️ ${result.computation_time.toFixed(2)}s`;

    document.getElementById('selectedStocksGrid').innerHTML = result.portfolio.selected_stocks
        .map(stock => `<div class="selected-stock-chip"><span>${stock}</span></div>`).join('');

    document.getElementById('metricQubits').textContent = result.qaoa_metrics.num_qubits;
    document.getElementById('metricDepth').textContent = result.qaoa_metrics.circuit_depth;
    document.getElementById('metricLayers').textContent = result.qaoa_metrics.qaoa_layers;
    document.getElementById('metricIterations').textContent = result.qaoa_metrics.iterations;

    // Sector diversification badge
    const sectorBadgeSection = document.getElementById('sectorBadgeSection');
    const sectorBadge = document.getElementById('sectorBadge');
    sectorBadgeSection.style.display = 'block';
    if (result.sector_diversification && result.sector_diversification.enabled) {
        sectorBadge.innerHTML = `🏢 Sector Diversification: <strong>ON</strong> (max ${result.sector_diversification.max_per_sector} per sector)`;
        sectorBadge.className = 'comparison-match-badge match';
    } else {
        sectorBadge.innerHTML = '🏢 Sector Diversification: <strong>OFF</strong> (unconstrained)';
        sectorBadge.className = 'comparison-match-badge mismatch';
    }

    // Classical vs Quantum comparison
    if (result.comparison) {
        const comp = result.comparison;
        document.getElementById('comparisonSection').style.display = 'block';

        const badge = document.getElementById('comparisonMatchBadge');
        badge.innerHTML = comp.results_match
            ? '✅ Both methods found the <strong>same optimal portfolio</strong>'
            : '⚠️ Methods found <strong>different portfolios</strong> — QAOA may need more iterations';
        badge.className = `comparison-match-badge ${comp.results_match ? 'match' : 'mismatch'}`;

        // Populate comparison columns
        const setCell = (id, val) => document.getElementById(id).textContent = val;
        setCell('classicalStocks', comp.classical.selected_stocks.join(', '));
        setCell('classicalReturn', `${(comp.classical.expected_return * 100).toFixed(2)}%`);
        setCell('classicalRisk', `${(comp.classical.portfolio_risk * 100).toFixed(2)}%`);
        setCell('classicalSharpe', comp.classical.sharpe_ratio.toFixed(3));
        setCell('classicalCost', comp.classical.optimal_cost.toFixed(4));
        setCell('classicalTime', `${comp.classical.computation_time.toFixed(4)}s`);
        setCell('qaoaStocks', comp.qaoa.selected_stocks.join(', '));
        setCell('qaoaReturn', `${(comp.qaoa.expected_return * 100).toFixed(2)}%`);
        setCell('qaoaRisk', `${(comp.qaoa.portfolio_risk * 100).toFixed(2)}%`);
        setCell('qaoaSharpe', comp.qaoa.sharpe_ratio.toFixed(3));
        setCell('qaoaCost', comp.qaoa.optimal_cost.toFixed(4));
        setCell('qaoaTime', `${comp.qaoa.computation_time.toFixed(4)}s`);
    }

    // Stock metrics table
    document.querySelector('#stockMetricsTable tbody').innerHTML = Object.entries(result.stock_metrics)
        .map(([ticker, m]) => `
            <tr>
                <td>${ticker}</td>
                <td>${(m.expected_return * 100).toFixed(2)}%</td>
                <td>${(m.volatility * 100).toFixed(2)}%</td>
                <td class="${m.selected ? 'status-selected' : 'status-not-selected'}">${m.selected ? '✓ Selected' : '—'}</td>
            </tr>
        `).join('');
}

function setLoadingState(loading) {
    state.isLoading = loading;
    const btnText = elements.optimizeBtn.querySelector('.btn-text');
    const btnLoading = elements.optimizeBtn.querySelector('.btn-loading');
    const btnIcon = elements.optimizeBtn.querySelector('.btn-icon');
    btnText.style.display = loading ? 'none' : 'inline';
    btnIcon.style.display = loading ? 'none' : 'inline';
    btnLoading.style.display = loading ? 'flex' : 'none';
    elements.optimizeBtn.disabled = loading;
}

function showStockLoading() {
    elements.stockGrid.innerHTML = '<div class="loading-placeholder"><div class="spinner"></div><p>Loading stocks...</p></div>';
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorToast.style.display = 'flex';
    setTimeout(hideError, 5000);
}

function hideError() { elements.errorToast.style.display = 'none'; }
window.hideError = hideError;

function getDemoStocks() {
    return [
        { ticker: 'RELIANCE', name: 'Reliance Industries', sector: 'Energy' },
        { ticker: 'TCS', name: 'Tata Consultancy Services', sector: 'IT' },
        { ticker: 'INFY', name: 'Infosys', sector: 'IT' },
        { ticker: 'HDFCBANK', name: 'HDFC Bank', sector: 'Banking' },
        { ticker: 'ICICIBANK', name: 'ICICI Bank', sector: 'Banking' },
        { ticker: 'HINDUNILVR', name: 'Hindustan Unilever', sector: 'FMCG' },
        { ticker: 'SBIN', name: 'State Bank of India', sector: 'Banking' },
        { ticker: 'BHARTIARTL', name: 'Bharti Airtel', sector: 'Telecom' },
        { ticker: 'KOTAKBANK', name: 'Kotak Mahindra Bank', sector: 'Banking' },
        { ticker: 'LT', name: 'Larsen & Toubro', sector: 'Infrastructure' }
    ];
}

document.addEventListener('DOMContentLoaded', init);
