const cards = [
  {
    title: "Auto-pay Rules",
    value: "12 active",
    detail: "Electricity, telecom, internet, and approved vendor billers",
  },
  {
    title: "Pending Reviews",
    value: "3 flagged",
    detail: "Threshold breaches and unusual amount variance",
  },
  {
    title: "Payments Today",
    value: "27 processed",
    detail: "24 succeeded, 2 pending, 1 awaiting approval",
  },
];

const reviews = [
  {
    vendor: "Tata Power",
    amount: "INR 6,400.00",
    reason: "Above policy threshold",
  },
  {
    vendor: "Airtel Business",
    amount: "INR 18,200.00",
    reason: "Historical variance detected",
  },
];

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="hero">
        <p className="eyebrow">A-FRA MVP</p>
        <h1>Deterministic bill payments with audit-ready controls.</h1>
        <p className="hero-copy">
          Define payment rules, monitor execution, and route anomalies into a
          human approval queue without losing traceability.
        </p>
      </section>

      <section className="card-grid">
        {cards.map((card) => (
          <article className="stat-card" key={card.title}>
            <p className="card-label">{card.title}</p>
            <h2>{card.value}</h2>
            <p>{card.detail}</p>
          </article>
        ))}
      </section>

      <section className="content-grid">
        <article className="panel">
          <div className="panel-header">
            <p className="panel-kicker">Policy Builder</p>
            <h3>Default SME rule profile</h3>
          </div>
          <ul className="rule-list">
            <li>Auto-pay electricity bills under INR 10,000</li>
            <li>Flag any telecom bill over historical median by 20%</li>
            <li>Require HITL approval for new vendor references</li>
          </ul>
        </article>

        <article className="panel">
          <div className="panel-header">
            <p className="panel-kicker">Review Queue</p>
            <h3>Human-in-the-loop decisions</h3>
          </div>
          <div className="review-list">
            {reviews.map((review) => (
              <div className="review-row" key={`${review.vendor}-${review.amount}`}>
                <div>
                  <strong>{review.vendor}</strong>
                  <p>{review.reason}</p>
                </div>
                <span>{review.amount}</span>
              </div>
            ))}
          </div>
        </article>
      </section>
    </main>
  );
}

