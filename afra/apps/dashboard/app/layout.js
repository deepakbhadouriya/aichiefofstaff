import "./globals.css";

export const metadata = {
  title: "A-FRA Dashboard",
  description: "Autonomous Financial Reconciliation Agent operations dashboard",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

