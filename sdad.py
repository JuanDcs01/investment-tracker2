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

