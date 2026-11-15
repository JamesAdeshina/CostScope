import {
  AdminDashboard,
} from "@/components/admin/admin-dashboard";

import {
  AdminLogin,
} from "@/components/admin/admin-login";

import {
  isAdminAuthenticated,
} from "@/lib/admin/session";


export default async function
AdminPage() {
  const authenticated =
    await isAdminAuthenticated();

  return (
    <main className="min-h-screen bg-zinc-50">
      <div className="mx-auto max-w-4xl px-6 py-16 lg:px-8">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-zinc-500">
          CostScope
        </p>

        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-zinc-950">
          Administration
        </h1>

        <p className="mt-3 max-w-2xl text-zinc-600">
          Manage the CostScope data warehouse and trigger a complete refresh from official source datasets.
        </p>

        {authenticated ? (
          <AdminDashboard />
        ) : (
          <AdminLogin />
        )}
      </div>
    </main>
  );
}
