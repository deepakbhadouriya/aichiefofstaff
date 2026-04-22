const cards = [
  {
    title: "Personas",
    value: "2 profiles",
    detail: "Seeded demo access plus live connector mode for actual operators",
  },
  {
    title: "Realtime Connectors",
    value: "6 tracked",
    detail: "BBPS, ERP sync, and communications status across demo and live modes",
  },
  {
    title: "Seeded Records",
    value: "Demo-ready",
    detail: "Invoices, payment history, and approvals available until actual sources go live",
  },
];

const personas = [
  {
    label: "Persona 1",
    name: "Demo Finance Manager",
    mode: "demo_seeded",
    detail:
      "Uses seeded bills, vendor history, and review queue data so prospects and internal teams can explore the workflow immediately.",
  },
  {
    label: "Persona 2",
    name: "Actual Finance Operator",
    mode: "live_connectors",
    detail:
      "Uses real connector definitions with realtime status monitoring, seeded fallback, and production-oriented approval controls.",
  },
];

const connectors = [
  {
    product: "Setu BBPS",
    status: "Healthy demo preview",
    detail: "Mock realtime polling for demo_user and live-ready credentials path for actual_user",
  },
  {
    product: "ERP / Ledger Sync",
    status: "Awaiting tenant mapping",
    detail: "Seeded journal events today, live posting path ready for onboarding",
  },
  {
    product: "Mailbox Sync",
    status: "OAuth pending",
    detail: "Seeded invoice threads visible now, realtime mail sync ready for activation",
  },
];

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="hero">
        <p className="eyebrow">A-FRA MVP</p>
        <h1>Deterministic bill payments with audit-ready controls.</h1>
        <p className="hero-copy">
          Define payment rules, monitor realtime connector readiness, and switch
          between a seeded demo persona and an actual operator persona without
          losing traceability.
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
            <p className="panel-kicker">User Personas</p>
            <h3>Demo and actual-user operating modes</h3>
          </div>
          <div className="persona-list">
            {personas.map((persona) => (
              <div className="persona-row" key={persona.name}>
                <p className="panel-kicker">{persona.label}</p>
                <strong>{persona.name}</strong>
                <p>{persona.mode}</p>
                <p>{persona.detail}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <p className="panel-kicker">Realtime Integrations</p>
            <h3>Connector readiness and fallback strategy</h3>
          </div>
          <div className="review-list">
            {connectors.map((connector) => (
              <div className="review-row" key={connector.product}>
                <div>
                  <strong>{connector.product}</strong>
                  <p>{connector.detail}</p>
                </div>
                <span>{connector.status}</span>
              </div>
            ))}
          </div>
        </article>
      </section>
    </main>
  );
}
