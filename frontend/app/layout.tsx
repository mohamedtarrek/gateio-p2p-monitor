/**
 * Root Layout
 * Provides the HTML structure and metadata for the application.
 */

export const metadata = {
  title: 'Gate.io P2P Monitor',
  description: 'Real-time USDT/EGP P2P price monitoring with Telegram notifications',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
