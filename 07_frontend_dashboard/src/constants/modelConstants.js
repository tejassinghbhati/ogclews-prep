export const DEFAULT_MACRO_PARAMS = {
  // Household Demographics
  S: { value: 80, min: 40, max: 100, label: 'Overlapping Generations (S)', unit: 'periods', description: 'Number of model periods representing a lifetime.' },
  J: { value: 7, options: [1,2,3,7], label: 'Skill Types (J)', unit: '', description: 'Number of distinct household skill groups.' },
  lambdas: { value: '0.25,0.25,0.20,0.10,0.10,0.05,0.05', label: 'Labor Income Shares (λ)', unit: '', description: 'Comma-separated fractions summing to 1.0.' },

  // Fiscal Policy
  tau_b: { value: 21.0, min: 0, max: 50, label: 'Corporate Income Tax Rate (τ_b)', unit: '%', description: 'Statutory corporate tax rate applied to capital income.' },
  tau_payroll: { value: 13.5, min: 0, max: 30, label: 'Payroll Tax Rate (τ_p)', unit: '%', description: 'Combined employer and employee payroll tax rate.' },
  alpha_G: { value: 0.178, min: 0.00, max: 0.30, step: 0.001, label: 'Govt. Spending Share (α_G)', unit: 'fraction of GDP', description: 'Government consumption as a share of output.' },
  budget_closure: { value: 'debt', options: ['debt','tax','mixed'], label: 'Budget Closure Rule', unit: '', description: 'Mechanism used to satisfy the government budget constraint.' },

  // Economic Parameters
  delta: { value: 0.05, min: 0.01, max: 0.15, step: 0.001, label: 'Capital Depreciation Rate (δ)', unit: 'annual', description: 'Fraction of capital stock that depreciates each period.' },
  sigma: { value: 1.5, min: 0.5, max: 3.0, step: 0.1, label: 'Risk Aversion Coefficient (σ)', unit: '', description: 'Coefficient of relative risk aversion in utility function.' },
  delta_tau_annual: { value: 0.04, min: 0.04, max: 0.06, step: 0.001, label: 'TFP Growth Proxy (Δτ)', unit: 'CLEWS-injected', readOnly: true, description: 'Annual TFP growth derived from CLEWS capacity expansion. Injected by ETL pipeline.' },

  // Solver Settings
  T_S: { value: 320, min: 1, max: 800, label: 'Transition Periods (T_S)', unit: 'periods', description: 'Number of periods in the transition path computation.' },
  maxiter: { value: 200, min: 10, max: 1000, label: 'Max Solver Iterations', unit: '', description: 'Maximum iterations for the inner SS/TP solver.' },
  nu: { value: 0.4, min: 0.1, max: 1.0, step: 0.05, label: 'Dampening Parameter (ν)', unit: '', description: 'Step-size dampening for convergence stability.' },
};

export const DEFAULT_CLEWS_PARAMS = {
  // Energy Capacities
  max_solar_gw: { value: 0.8, min: 0, max: 5.0, step: 0.1, label: 'Max Solar Capacity', unit: 'GW', description: 'Upper bound on installed solar photovoltaic capacity.' },
  max_wind_gw: { value: 0.4, min: 0, max: 3.0, step: 0.1, label: 'Max Wind Capacity', unit: 'GW', description: 'Upper bound on installed wind generation capacity.' },
  retire_diesel: { value: 2035, options: [2028,2030,2032,2035,2038,2040], label: 'Diesel Phase-out Year', unit: '', description: 'Year by which all open-cycle diesel generation must be retired.' },
  renewable_bound: { value: 60, min: 20, max: 100, label: 'Grid Renewables Share', unit: '%', description: 'Minimum renewable energy fraction of total grid generation.' },

  // Emissions
  emission_cap_mt: { value: 0.547, min: 0.1, max: 3.3, step: 0.01, label: 'Annual CO₂ Cap', unit: 'Mt CO₂', description: 'Hard annual cap on system-wide carbon dioxide emissions.' },
  carbon_price: { value: 45.0, min: 0, max: 200, label: 'Carbon Price', unit: 'USD/ton', description: 'Economy-wide carbon price applied as a penalty in OSeMOSYS cost function.' },
  tau_c: { value: 0.00165, min: 0, max: 0.01, step: 0.00001, label: 'Emission Tax Proxy (τ_c)', unit: 'OG-Core injected', readOnly: true, description: 'Emission penalty proxy for OG-Core fiscal sector. Derived from CLEWS emissions.' },

  // Water & Land
  water_constraint: { value: 0.28, min: 0.05, max: 2.0, step: 0.01, label: 'Water Usage Limit', unit: 'km³/yr', description: 'Annual freshwater consumption ceiling across energy and agricultural sectors.' },
  land_use_cap: { value: 120, min: 10, max: 500, label: 'Renewable Land Ceiling', unit: 'km²', description: 'Maximum land area allocable to solar and wind installations.' },
};

export const ETL_MAPPING = [
  { clews: 'TotalCapacityAnnual.csv', var: 'Energy Capacity (GW)', transform: 'GW→TW, min-max [0.04,0.06]', og: 'delta_tau_annual', color: 'emerald' },
  { clews: 'AnnualTechnologyEmission.csv', var: 'CO₂ Emissions (Mt)', transform: 'linear scalar ×0.0005', og: 'tau_c', color: 'amber' },
  { clews: 'TotalDiscountedCost.csv', var: 'System Cost (MUSD)', transform: 'GDP ratio, min-max [0.03,0.08]', og: 'alpha_G', color: 'blue' },
];

export const CONVERGENCE_EPSILON = 1e-4;
export const MAX_ITERATIONS = 25;
