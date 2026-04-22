"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const API_BASE_URL = "http://127.0.0.1:8000";

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company_name: "",
  });
  const [onboardingStatus, setOnboardingStatus] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleStartOnboarding = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (!response.ok) throw new Error("Failed to start onboarding");
      const data = await response.json();
      setOnboardingStatus(data);
      setStep(2);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteOnboarding = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/complete`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Profile-ID": onboardingStatus.profile_id,
        },
      });
      if (!response.ok) throw new Error("Failed to complete onboarding");
      setStep(3);
      // In a real app, we'd save the profile_id to local storage or session
      setTimeout(() => {
        router.push("/");
      }, 2000);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectIntegration = async (integrationId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/link-integration`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Profile-ID": onboardingStatus.profile_id,
        },
        body: JSON.stringify({
          integration_id: integrationId,
          config: { mock: true }
        }),
      });
      if (!response.ok) throw new Error("Failed to link integration");
      alert(`${integrationId} connected successfully!`);
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <main className="page-shell onboarding-container">
      <article className="panel onboarding-card animate-fade-in">
        <div className="onboarding-steps">
          <div className={`onboarding-step-dot ${step >= 1 ? "active" : ""}`} />
          <div className={`onboarding-step-dot ${step >= 2 ? "active" : ""}`} />
          <div className={`onboarding-step-dot ${step >= 3 ? "active" : ""}`} />
        </div>

        {step === 1 && (
          <div className="onboarding-content">
            <div className="panel-header">
              <p className="panel-kicker">Step 1 of 3</p>
              <h3>Welcome to A-FRA</h3>
              <p className="hero-copy">Let's set up your autonomous finance operations.</p>
            </div>
            <form className="onboarding-form" onSubmit={handleStartOnboarding}>
              <div className="form-group">
                <label htmlFor="name">Full Name</label>
                <input
                  id="name"
                  name="name"
                  className="form-input"
                  placeholder="e.g. Rahul Sharma"
                  required
                  value={formData.name}
                  onChange={handleChange}
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">Work Email</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  className="form-input"
                  placeholder="name@company.com"
                  required
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
              <div className="form-group">
                <label htmlFor="company_name">Company Name</label>
                <input
                  id="company_name"
                  name="company_name"
                  className="form-input"
                  placeholder="e.g. Acme Corp"
                  required
                  value={formData.company_name}
                  onChange={handleChange}
                />
              </div>
              <button className="primary-button" type="submit" disabled={loading}>
                {loading ? "Initializing..." : "Get Started"}
              </button>
            </form>
          </div>
        )}

        {step === 2 && (
          <div className="onboarding-content">
            <div className="panel-header">
              <p className="panel-kicker">Step 2 of 3</p>
              <h3>Connect Integrations</h3>
              <p className="hero-copy">
                A-FRA needs access to your mailbox and payment rails to automate reconciliation.
              </p>
            </div>
            <div className="detail-stack">
              <div className="review-row">
                <div>
                  <strong>Google Workspace</strong>
                  <p>Read invoices and vendor communication</p>
                </div>
                <button className="secondary-button" type="button" onClick={() => handleConnectIntegration("gmail")}>Connect</button>
              </div>
              <div className="review-row">
                <div>
                  <strong>Setu BBPS</strong>
                  <p>Programmatic utility payments</p>
                </div>
                <button className="secondary-button" type="button" onClick={() => handleConnectIntegration("setu")}>Connect</button>
              </div>
            </div>
            <div className="action-row" style={{ marginTop: "32px" }}>
              <button className="primary-button" onClick={handleCompleteOnboarding} disabled={loading}>
                {loading ? "Saving..." : "Continue to Dashboard"}
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="onboarding-success">
            <div className="onboarding-success-icon">✓</div>
            <h3>Setup Complete!</h3>
            <p className="hero-copy">
              Redirecting you to your new finance operations console...
            </p>
          </div>
        )}
      </article>
    </main>
  );
}
