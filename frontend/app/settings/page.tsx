import {
  Bell,
  User,
  Palette,
  Shield,
  Settings as SettingsIcon,
} from "lucide-react";

export default function SettingsPage() {
  return (
    <main className="min-h-screen bg-[#050a18] text-white">
      <div className="mx-auto max-w-[1200px] space-y-8 px-6 py-10 lg:px-10">

        <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-[#152342] to-[#081122] p-8">

          <span className="rounded-full bg-blue-500/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-blue-400">
            Account
          </span>

          <h1 className="mt-5 text-4xl font-extrabold">
            Settings
          </h1>

          <p className="mt-3 text-slate-400">
            Manage your FinPilot AI account and preferences.
          </p>

        </section>

        {/* Profile */}
        <section className="rounded-3xl border border-white/10 bg-[#0d162b] p-7">

          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-600 text-xl font-bold">
              A
            </div>

            <div>
              <h2 className="text-xl font-bold">
                Akshat Kasliwal
              </h2>

              <p className="text-sm text-slate-400">
                Premium Plan
              </p>
            </div>
          </div>

        </section>

        {/* Settings */}
        <div className="space-y-4">

          <Setting
            icon={<User />}
            title="Profile"
            description="Manage your personal information and account details."
          />

          <Setting
            icon={<Bell />}
            title="Notifications"
            description="Configure price alerts and market notifications."
          />

          <Setting
            icon={<Palette />}
            title="Appearance"
            description="Customize the look and feel of FinPilot AI."
          />

          <Setting
            icon={<Shield />}
            title="Privacy & Security"
            description="Manage account security and privacy preferences."
          />

          <Setting
            icon={<SettingsIcon />}
            title="Application Preferences"
            description="Configure market, currency and dashboard preferences."
          />

        </div>

      </div>
    </main>
  );
}

function Setting({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <button className="flex w-full items-center gap-5 rounded-2xl border border-white/10 bg-[#0d162b] p-6 text-left transition hover:border-blue-500/30 hover:bg-[#111d38]">

      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
        {icon}
      </div>

      <div className="flex-1">
        <h3 className="font-semibold">
          {title}
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          {description}
        </p>
      </div>

      <span className="text-slate-500">
        →
      </span>

    </button>
  );
}