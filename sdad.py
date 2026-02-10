      <div class="col">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 opacity-75">Ganancia Hoy</h6>
            <h3
              class="card-title mb-0 {% if portfolio.today_gain >= 0 %}text-success{% else %}text-danger{% endif %}"
            >
              {{ portfolio.today_gain|currency }}
              <small class="fs-6">
                ({{ portfolio.today_gain_percentage|percentage }})
              </small>
            </h3>
          </div>
        </div>
      </div>

      <div class="col">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Retorno Neto (Real)</h6>
            <h3
              class="card-title mb-0 {% if portfolio.net_return >= 0 %}text-success{% else %}text-danger{% endif %}"
            >
              {{ portfolio.net_return|currency }}
              <small class="fs-6">
                ({{ portfolio.net_return_percentage|percentage }})
              </small>
            </h3>
          </div>
        </div>
      </div>













<!-- Portfolio Summary Cards -->
<div class="row g-3 mb-4 row-cols-1 row-cols-md-5 justify-content-center">    
  <div class="col">
      <div class="card">
        <div class="card-body">
          <h6 class="card-subtitle mb-2 opacity-75">Total Invertido</h6>
          <h3 class="card-title mb-0">
            {{ portfolio.total_invested|currency }}
          </h3>
        </div>
      </div>
    </div>
    <div class="col">
      <div class="card">
        <div class="card-body">
          <h6 class="card-subtitle mb-2 opacity-75">Valor Actual de Mercado</h6>
          <h3 class="card-title mb-0">
            {{ portfolio.current_market_value|currency }}
          </h3>
        </div>
      </div>
    </div>
    <div class="col">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Ganancia no Realizada</h6>
            <h3
              class="card-title mb-0 {% if portfolio.total_market_gain >= 0 %}text-success{% else %}text-danger{% endif %}"
            >
              {{ portfolio.total_market_gain|currency }}
              <small class="fs-6">
                ({{ portfolio.market_gain_percentage|percentage }})
              </small>
            </h3>
          </div>
        </div>
      </div>
    </div>


                <td class="text-end">{{ portfolio.total_cost_base|currency }}</td>
                <td class="text-end">{{ portfolio.total_comission|currency }}</td>








ddddddddddddddddddddddddddddddd





<!-- Portfolio Summary Cards - 3 Cards -->
  <div class="row g-3 mb-4">
    <!-- Total Invertido -->
    <div class="col-md-4">
      <div class="card">
        <div class="card-body">
          <h6 class="card-subtitle mb-2 text-muted">Total Invertido</h6>
          <h3 class="card-title mb-0">
            {{ portfolio.total_invested|currency }}
          </h3>
        </div>
      </div>
    </div>

    <!-- Valor Actual de Mercado -->
    <div class="col-md-4">
      <div class="card">
        <div class="card-body">
          <h6 class="card-subtitle mb-2 text-muted">Valor Actual de Mercado</h6>
          <h3 class="card-title mb-0">
            {{ portfolio.current_market_value|currency }}
          </h3>
        </div>
      </div>
    </div>

    <!-- Ganancia No Realizada -->
    <div class="col-md-4">
      <div class="card">
        <div class="card-body">
          <h6 class="card-subtitle mb-2 text-muted">Ganancia no Realizada</h6>
          <h3
            class="card-title mb-0 {% if portfolio.unrealized_gain >= 0 %}text-success{% else %}text-danger{% endif %}"
          >
            {{ portfolio.unrealized_gain|currency }}
            <small class="fs-6">
              ({{ portfolio.unrealized_gain_percentage|percentage }})
            </small>
          </h3>
          <small class="text-muted">Posición actual</small>
        </div>
      </div>
    </div>
  </div>