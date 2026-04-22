"use client";

import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000";

const PERSONA_CHOICES = [
  {
    id: "demo_user",
    label: "Demo Finance Manager",
    summary: "Seeded workflows, happy paths, and review cases ready to click through.",
  },
  {
    id: "actual_user",
    label: "Actual Finance Operator",
    summary: "Live-ready connector mode that stays safe until real credentials are onboarded.",
  },
];

async function callApi(path, { method = "GET", profileId = "demo_user", body } = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      "X-Tenant-ID": "demo-tenant",
      "X-Profile-ID": profileId,
      "X-Request-ID": `ui-${profileId}-${Date.now()}`,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }

  return response.json();
}

function formatMoney(amountMinor, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(amountMinor / 100);
}

export default function HomePage() {
  const [selectedProfile, setSelectedProfile] = useState("demo_user");
  const [sessionStarted, setSessionStarted] = useState(false);
  const [profile, setProfile] = useState(null);
  const [scenarios, setScenarios] = useState([]);
  const [payments, setPayments] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [integrations, setIntegrations] = useState([]);
  const [workflowDetail, setWorkflowDetail] = useState(null);
  const [seedResult, setSeedResult] = useState(null);
  const [statusMessage, setStatusMessage] = useState("Choose a persona to start the interactive demo.");
  const [loading, setLoading] = useState(false);

  async function refreshConsole(profileId = selectedProfile) {
    setLoading(true);
    try {
      const [profileData, scenarioData, paymentData, reviewData, integrationData] = await Promise.all([
        callApi("/api/v1/profiles/me", { profileId }),
        callApi("/api/v1/demo/scenarios", { profileId }),
        callApi("/api/v1/payments", { profileId }),
        callApi("/api/v1/reviews", { profileId }),
        callApi("/api/v1/integrations/realtime", { profileId }),
      ]);
      setProfile(profileData);
      setScenarios(scenarioData.filter((item) => item.persona === profileId));
      setPayments(paymentData);
      setReviews(reviewData);
      setIntegrations(integrationData.connectors);
      setStatusMessage(`Loaded ${profileData.display_name} console data.`);
    } catch (error) {
      setStatusMessage(`Unable to load console data: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function startSession(profileId) {
    setSelectedProfile(profileId);
    setSessionStarted(true);
    await refreshConsole(profileId);
  }

  async function handleSeed() {
    setLoading(true);
    try {
      const seeded = await callApi("/api/v1/demo/seed", {
        method: "POST",
        profileId: selectedProfile,
      });
      setSeedResult(seeded);
      setStatusMessage(`Seeded ${seeded.scenario_count} demo scenarios for ${selectedProfile}.`);
      await refreshConsole(selectedProfile);
    } catch (error) {
      setStatusMessage(`Seeding failed: ${error.message}`);
      setLoading(false);
    }
  }

  async function handleWorkflowOpen(workflowId) {
    setLoading(true);
    try {
      const workflow = await callApi(`/api/v1/workflows/${workflowId}`, { profileId: selectedProfile });
      setWorkflowDetail(workflow);
      setStatusMessage(`Loaded workflow ${workflowId}.`);
    } catch (error) {
      setStatusMessage(`Could not load workflow: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleReviewDecision(workflowId, action) {
    setLoading(true);
    try {
      await callApi(`/api/v1/reviews/${workflowId}/${action}`, {
        method: "POST",
        profileId: selectedProfile,
      });
      setStatusMessage(`${action === "approve" ? "Approved" : "Rejected"} ${workflowId}.`);
      await refreshConsole(selectedProfile);
      await handleWorkflowOpen(workflowId);
    } catch (error) {
      setStatusMessage(`Review action failed: ${error.message}`);
      setLoading(false);
    }
  }

  useEffect(() => {
    if (sessionStarted) {
      refreshConsole(selectedProfile);
    }
  }, [selectedProfile]);

  const cards = [
    {
      title: "Interactive Session",
      value: sessionStarted ? profile?.display_name || "Active" : "Waiting",
      detail: sessionStarted
        ? `Signed in as ${selectedProfile} with live API data`
        : "Sign in with a persona to open the demo console",
    },
    {
      title: "Review Queue",
      value: `${reviews.length} pending`,
      detail: "Approve or reject threshold breaches and weak-evidence vendor scenarios from the UI",
    },
    {
      title: "Payments",
      value: `${payments.length} loaded`,
      detail: "Seeded outcomes for demo flows or live-ready records for actual operators",
    },
  ];

  return (
    <main className="page-shell">
      <section className="hero">
        <p className="eyebrow">A-FRA MVP</p>
        <h1>Interactive finance ops console for seeded and live-ready flows.</h1>
        <p className="hero-copy">
          Sign in as a persona, seed demo workflows, inspect connector status,
          and resolve review items without leaving the app.
        </p>
      </section>

      <section className="content-grid">
        <article className="panel login-panel">
          <div className="panel-header">
            <p className="panel-kicker">Sign In</p>
            <h3>Select a persona</h3>
          </div>
          <div className="persona-list">
            {PERSONA_CHOICES.map((persona) => (
              <button
                className={`persona-card-button ${selectedProfile === persona.id ? "active" : ""}`}
                key={persona.id}
                onClick={() => startSession(persona.id)}
                type="button"
              >
                <span className="panel-kicker">{persona.id}</span>
                <strong>{persona.label}</strong>
                <span>{persona.summary}</span>
              </button>
            ))}
          </div>
          <div className="action-row">
            <button className="primary-button" onClick={handleSeed} type="button" disabled={!sessionStarted || loading}>
              Seed Demo Data
            </button>
            <button className="secondary-button" onClick={() => refreshConsole(selectedProfile)} type="button" disabled={!sessionStarted || loading}>
              Refresh Console
            </button>
          </div>
          <p className="status-banner">{loading ? "Working..." : statusMessage}</p>
          {seedResult ? (
            <div className="mini-summary">
              <strong>Latest seed result</strong>
              <p>{seedResult.scenario_count} scenarios loaded</p>
              <p>{seedResult.payment_count} payments ready</p>
              <p>{seedResult.review_queue_count} reviews awaiting action</p>
            </div>
          ) : null}
        </article>

        <article className="panel">
          <div className="panel-header">
            <p className="panel-kicker">Active Profile</p>
            <h3>{profile?.display_name || "No session yet"}</h3>
          </div>
          {profile ? (
            <div className="detail-stack">
              <p>{profile.description}</p>
              <p>Mode: {profile.operating_mode}</p>
              <p>Capabilities: {profile.capabilities.join(", ")}</p>
              <p>{profile.integration_status_summary}</p>
            </div>
          ) : (
            <p className="empty-state">Choose `demo_user` or `actual_user` to load the operator console.</p>
          )}
        </article>
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
            <p className="panel-kicker">Seeded Scenarios</p>
            <h3>Happy and negative SME walkthroughs</h3>
          </div>
          <div className="review-list">
            {scenarios.map((scenario) => (
              <div className="review-row" key={scenario.id}>
                <div>
                  <strong>{scenario.title}</strong>
                  <p>{scenario.walkthrough_hint}</p>
                </div>
                <span>{scenario.expected_outcome}</span>
              </div>
            ))}
            {!scenarios.length ? <p className="empty-state">Sign in to load seeded scenario guidance.</p> : null}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <p className="panel-kicker">Realtime Integrations</p>
            <h3>Connector readiness for SMEs</h3>
          </div>
          <div className="review-list">
            {integrations.map((connector) => (
              <div className="review-row" key={connector.id}>
                <div>
                  <strong>{connector.product_name}</strong>
                  <p>{connector.status_message}</p>
                </div>
                <span>{connector.status}</span>
              </div>
            ))}
            {!integrations.length ? <p className="empty-state">Connector status loads after sign-in.</p> : null}
          </div>
        </article>
      </section>

      <section className="content-grid">
        <article className="panel">
          <div className="panel-header">
            <p className="panel-kicker">Payments</p>
            <h3>Executed or seeded payment outcomes</h3>
          </div>
          <div className="table-list">
            {payments.map((payment) => (
              <button
                className="table-row-button"
                key={payment.id}
                onClick={() => handleWorkflowOpen(payment.workflow_run_id)}
                type="button"
              >
                <div>
                  <strong>{payment.vendor_name}</strong>
                  <p>{payment.integration_mode}</p>
                </div>
                <span>{formatMoney(payment.amount_minor, payment.currency)}</span>
              </button>
            ))}
            {!payments.length ? <p className="empty-state">No payments loaded yet. Seed the demo to populate this view.</p> : null}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <p className="panel-kicker">Review Queue</p>
            <h3>Human-in-the-loop actions</h3>
          </div>
          <div className="review-list">
            {reviews.map((review) => (
              <div className="action-card" key={review.workflow_run_id}>
                <div>
                  <strong>{review.vendor_name}</strong>
                  <p>{review.reason}</p>
                  <p>{formatMoney(review.amount_minor, "INR")}</p>
                </div>
                <div className="action-row">
                  <button className="secondary-button" onClick={() => handleWorkflowOpen(review.workflow_run_id)} type="button">
                    Inspect
                  </button>
                  <button className="primary-button" onClick={() => handleReviewDecision(review.workflow_run_id, "approve")} type="button">
                    Approve
                  </button>
                  <button className="danger-button" onClick={() => handleReviewDecision(review.workflow_run_id, "reject")} type="button">
                    Reject
                  </button>
                </div>
              </div>
            ))}
            {!reviews.length ? <p className="empty-state">No pending reviews for the current persona.</p> : null}
          </div>
        </article>
      </section>

      <section className="content-grid">
        <article className="panel">
          <div className="panel-header">
            <p className="panel-kicker">Workflow Detail</p>
            <h3>Execution trace</h3>
          </div>
          {workflowDetail ? (
            <div className="detail-stack">
              <p>Workflow ID: {workflowDetail.id}</p>
              <p>State: {workflowDetail.current_state}</p>
              <p>Decision: {workflowDetail.decision}</p>
              <p>X-Request-ID: {workflowDetail.x_request_id}</p>
              <p>Payment Intent: {workflowDetail.payment_intent_id || "Not created"}</p>
              <p>Payment ID: {workflowDetail.payment_id || "Not created"}</p>
              <p>Ledger Sync: {workflowDetail.ledger_sync_id || "Not created"}</p>
              <div className="evidence-list">
                {workflowDetail.evidence.map((item, index) => (
                  <div className="evidence-card" key={`${item.source}-${index}`}>
                    <strong>{item.source}</strong>
                    <p>{item.summary}</p>
                    <span>Confidence: {Math.round(item.confidence * 100)}%</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="empty-state">Open a payment or review item to inspect the workflow.</p>
          )}
        </article>

        <article className="panel">
          <div className="panel-header">
            <p className="panel-kicker">How To Use</p>
            <h3>Clickable demo script</h3>
          </div>
          <ul className="rule-list">
            <li>Sign in as `demo_user` to load the seeded finance walkthrough.</li>
            <li>Click `Seed Demo Data` once to create happy-path and negative-path runs.</li>
            <li>Open a payment to inspect the completed workflow trace.</li>
            <li>Open a review item and approve it to watch the run move through payment and ledger sync.</li>
            <li>Switch to `actual_user` to inspect the live-ready connector posture for real SMEs.</li>
          </ul>
        </article>
      </section>
    </main>
  );
}
