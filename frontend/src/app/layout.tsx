import type {
  Metadata,
} from "next";

import "./globals.css";


export const metadata: Metadata = {
  title: "CostScope",
  description:
    "Explore UK cost-of-living indicators including rent, earnings, inflation and unemployment.",
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
