'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/', label: 'HOME' },
  { href: '/dashboard', label: 'DASHBOARD' },
  { href: '/playground', label: 'PLAYGROUND' },
  { href: '/simulator', label: 'SIMULATOR' },
  { href: '/sessions', label: 'SESSIONS' },
  { href: '/compare', label: 'COMPARE' },
  { href: '/automata', label: 'AUTOMATA LAB' },
  { href: '/attack-lab', label: 'ATTACK LAB' },
  { href: '/analytics', label: 'ANALYTICS' },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-cream border-b border-cream-border">
      <div className="max-w-[1400px] mx-auto px-6 flex items-center justify-between h-12">
        <Link href="/" className="flex items-center gap-2">
          <span className="font-serif font-bold text-sm text-warm-text tracking-tight">
            DIGITAL DOPPELGÄNGER
          </span>
          <span className="text-[10px] font-mono text-warm-muted ml-1">
            BEHAVIORAL ANALYSIS v2.0
          </span>
        </Link>

        <nav className="flex items-center gap-0.5">
          {navItems.map((item) => {
            const isActive = pathname === item.href ||
              (item.href !== '/' && pathname.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-2.5 py-1.5 text-[10px] font-mono font-medium tracking-wide transition-colors ${
                  isActive
                    ? 'bg-forest text-white'
                    : 'text-warm-secondary hover:text-warm-text hover:bg-cream-dark'
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
