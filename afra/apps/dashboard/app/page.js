"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const API_BASE_URL = "http://127.0.0.1:8000";

const PERSONA_CHOICES = [
  { id: "demo_user", label: "Startup Founder", summary: "Pre-seed founder with chaotic SaaS subscriptions and utility bills." },
  { id: "actual_user", label: "Executive Owner", summary: "Established SME owner connecting real bank and workspace data." },
];

const CONNECTORS = [
  { id: "gmail", label: "Gmail", status: "active" },
  { id: "drive", label: "Drive", status: "active" },
  { id: "bank", label: "Banking", status: "active" },
  { id: "calendar", label: "Calendar", status: "idle" },
  { id: "sms", label: "SMS", status: "idle" },
];

export default function HomePage() {
  const router = useRouter();
  const [sessionStarted, setSessionStarted] = useState(false);
  const [selectedProfile, setSelectedProfile] = useState("demo_user");
  const [profile, setProfile] = useState(null);
  const [payments, setPayments] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [auditEvents, setAuditEvents] = useState([]);
  const [crm, setCrm] = useState({ contacts: [], recent_interactions: [], nudges: [] });
  const [statusMessage, setStatusMessage] = useState("Agent initialized. Awaiting executive command.");
  const [loading, setLoading] = useState(false);
  const [agentThinking, setAgentThinking] = useState(false);

  // Mock Executive Tasks
  const [tasks, setTasks] = useState([
    { id: "task-1", type: "calendar", title: "Board Meeting Prep", time: "2:00 PM", status: "autonomous" },
    { id: "task-2", type: "sms", title: "Vendor Payment Reminder", time: "4:30 PM", status: "pending" },
  ]);

  async function callApi(path, options = {}) {
    const { method = "GET", body, profileId = selectedProfile } = options;
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        "X-Profile-ID": profileId,
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function refreshAgent(profileId = selectedProfile) {
    setLoading(true);
    setAgentThinking(true);
    try {
      const [profileData, paymentData, reviewData, policyData, crmData] = await Promise.all([
        callApi("/api/v1/profiles/me", { profileId }),
        callApi("/api/v1/payments", { profileId }),
        callApi("/api/v1/reviews", { profileId }),
        callApi("/api/v1/policies", { profileId }),
        callApi("/api/v1/crm/snapshot", { profileId }),
      ]);
      setProfile(profileData);
      setPayments(paymentData);
      setReviews(reviewData);
      setPolicies(policyData);
      setCrm(crmData);
      setStatusMessage(`Agent synced with ${profileData.display_name}'s executive context.`);
    } catch (error) {
      setStatusMessage(`Sync failed: ${error.message}`);
    } finally {
      setLoading(false);
      setTimeout(() => setAgentThinking(false), 1000);
    }
  }

  function startSession(profileId) {
    setSelectedProfile(profileId);
    setSessionStarted(true);
    refreshAgent(profileId);
  }

  const formatMoney = (minor, cur = "INR") =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: cur }).format(minor / 100);

  return (
    <main className="page-shell">
      {/* Agentic Core */}
      <div className="agent-core-container animate-fade-in">
        <div 
          className={`agent-core ${agentThinking ? "thinking" : ""}`} 
          onClick={() => refreshAgent()}
          title="Click to re-sync agent brain"
        />
      </div>

      <header className="hero animate-slide-up" style={{ animationDelay: "0.1s" }}>
        <h1>CHIEF OF STAFF</h1>
        <p className="hero-copy">
          Autonomous Bill Ops & Executive Task Management. 
          Connected to your workspace, bank, and calendar.
        </p>
      </header>

      {/* Connectivity Hub */}
      <section className="panel glass-card animate-slide-up" style={{ animationDelay: "0.2s" }}>
        <div className="panel-header">
          <p className="panel-kicker">Agentic Context</p>
          <h3>Active Connectors</h3>
        </div>
        <div className="connectors-grid">
          {CONNECTORS.map((c) => (
            <div className={`connector-pill ${c.status === "active" ? "active" : ""}`} key={c.id}>
              <span className="connector-dot"></span>
              {c.label}
            </div>
          ))}
        </div>
      </section>

      {!sessionStarted ? (
        <section className="content-grid animate-slide-up" style={{ animationDelay: "0.3s" }}>
          <article className="panel">
            <div className="panel-header">
              <p className="panel-kicker">Initialize</p>
              <h3>Select Persona</h3>
            </div>
            <div className="persona-list">
              {PERSONA_CHOICES.map((p) => (
                <button className="persona-card-button" key={p.id} onClick={() => startSession(p.id)}>
                  <strong>{p.label}</strong>
                  <p>{p.summary}</p>
                </button>
              ))}
            </div>
          </article>
        </section>
      ) : (
        <>
          {/* Executive Briefing */}
          <section className="panel briefing-panel animate-slide-up" style={{ animationDelay: "0.3s", marginTop: "24px" }}>
            <div className="panel-header">
              <p className="panel-kicker">Briefing • {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
            </div>
            <p className="briefing-text">
              {profile?.display_name.split(' ')[0]}, I'm currently monitoring your <strong>Gmail</strong> for invoices. 
              Found <strong>{payments.length} scheduled payments</strong> for this week. 
              I've also prepared your <strong>Drive folder</strong> for the tax audit. 
              You have {reviews.length} anomalies needing executive sign-off.
            </p>
          </section>

          {/* Unified Agentic Feed */}
          <div className="content-grid">
            <section className="panel animate-slide-up" style={{ animationDelay: "0.4s" }}>
              <div className="panel-header">
                <p className="panel-kicker">Unified Feed</p>
                <h3>Active Intelligence Thread</h3>
              </div>
              <div className="agentic-feed">
                {/* Finance Items */}
                {payments.map(p => (
                  <div className="feed-item" key={p.id}>
                    <div className="feed-icon">₹</div>
                    <div>
                      <strong>Bill Paid: {p.vendor_name}</strong>
                      <p>Matched invoice from Gmail #234 to Drive receipt.</p>
                    </div>
                    <div className="trend-up">{formatMoney(p.amount_minor)}</div>
                  </div>
                ))}
                {/* Executive Tasks */}
                {tasks.map(t => (
                  <div className="feed-item" key={t.id}>
                    <div className="feed-icon">{t.type === 'calendar' ? '📅' : '📱'}</div>
                    <div>
                      <strong>{t.title}</strong>
                      <p>{t.status === 'autonomous' ? 'Agent is preparing context documents.' : 'Awaiting your direction.'}</p>
                    </div>
                    <div className="panel-kicker">{t.time}</div>
                  </div>
                ))}
                {/* Review Items */}
                {reviews.map(r => (
                  <div className="feed-item" key={r.workflow_run_id} style={{ borderColor: 'var(--gold)' }}>
                    <div className="feed-icon" style={{ color: 'var(--gold)' }}>⚠</div>
                    <div>
                      <strong>Anomaly: {r.vendor_name}</strong>
                      <p>Amount exceeds your autopay policy. Review needed.</p>
                    </div>
                    <button className="primary-button" style={{ padding: '8px 16px', fontSize: '0.8rem' }}>Review</button>
                  </div>
                ))}
              </div>
            </section>

            {/* Strategic Insights */}
            <section className="panel animate-slide-up" style={{ animationDelay: "0.5s" }}>
              <div className="panel-header">
                <p className="panel-kicker">Strategic Pulse</p>
                <h3>Autonomous Insights</h3>
              </div>
              <div className="stat-card" style={{ marginTop: '20px' }}>
                <p className="card-label">SaaS Burn Rate</p>
                <h2>₹1,24,000</h2>
                <p><span className="trend-down">↓ 8%</span> after I canceled idle seats.</p>
              </div>
              <div className="stat-card" style={{ marginTop: '20px' }}>
                <p className="card-label">Cash Runway</p>
                <h2>14 Months</h2>
                <p>Based on current burn and bank balance.</p>
              </div>
            </section>

            {/* Relationship Pulse (Executive CRM) */}
            <section className="panel animate-slide-up" style={{ animationDelay: "0.6s" }}>
              <div className="panel-header">
                <p className="panel-kicker">Relationship Pulse</p>
                <h3>Executive CRM</h3>
              </div>
              <div className="agentic-feed" style={{ marginTop: '20px' }}>
                {crm.contacts.map(contact => (
                  <div className="feed-item" key={contact.id} style={{ borderLeft: `4px solid ${contact.status === 'Stale' ? '#ff3366' : contact.status === 'Cooling' ? 'var(--gold)' : 'var(--accent)'}` }}>
                    <div className="feed-icon">{contact.name[0]}</div>
                    <div>
                      <strong>{contact.name} ({contact.company})</strong>
                      <p>{contact.summary}</p>
                      <span style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>Status: {contact.status} • Last: {new Date(contact.last_interaction_at).toLocaleDateString()}</span>
                    </div>
                    <button className="secondary-button" style={{ padding: '6px 12px', fontSize: '0.7rem' }}>Sync Activity</button>
                  </div>
                ))}
              </div>
              {crm.nudges.length > 0 && (
                <div className="mini-summary" style={{ background: 'rgba(255, 204, 0, 0.05)', borderColor: 'var(--gold)', marginTop: '24px' }}>
                  <p className="panel-kicker" style={{ color: 'var(--gold)' }}>Agent Nudges</p>
                  {crm.nudges.map((nudge, idx) => (
                    <p key={idx} style={{ fontSize: '0.9rem', marginBottom: '8px' }}>• {nudge}</p>
                  ))}
                </div>
              )}
            </section>
          </div>
        </>
      )}
    </main>
  );
}
