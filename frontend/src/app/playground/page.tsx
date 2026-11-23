'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { sessionsApi } from '@/lib/api';
import { useWebSocket } from '@/hooks/useWebSocket';
import EventTimeline from '@/components/EventTimeline';
import ClassificationBadge from '@/components/ClassificationBadge';
import ScoreBar from '@/components/ScoreBar';

const SHOP_PAGES = [
  { id: 'home', label: 'Home', path: '/' },
  { id: 'products', label: 'Products', path: '/products' },
  { id: 'product1', label: 'Wireless Headphones', path: '/products/1', price: '₹2,499' },
  { id: 'product2', label: 'Smart Watch', path: '/products/2', price: '₹4,999' },
  { id: 'product3', label: 'USB-C Hub', path: '/products/3', price: '₹1,299' },
  { id: 'search', label: 'Search', path: '/search' },
  { id: 'cart', label: 'Cart', path: '/cart' },
  { id: 'login', label: 'Login', path: '/login' },
  { id: 'checkout', label: 'Checkout', path: '/checkout' },
  { id: 'profile', label: 'Profile', path: '/profile' },
];

export default function PlaygroundPage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState('home');
  const [events, setEvents] = useState<any[]>([]);
  const [currentState, setCurrentState] = useState<any>(null);
  const [score, setScore] = useState<any>(null);
  const [sessionEnded, setSessionEnded] = useState(false);
  const eventCountRef = useRef(0);

  const { connected, send } = useWebSocket(
    sessionId ? `/ws/events/${sessionId}` : '',
    {
      autoConnect: false,
      onMessage: (data) => {
        setEvents(prev => [...prev, data]);
        setCurrentState(data.product_state);
      },
    }
  );

  const startSession = useCallback(async () => {
    try {
      const { session_id } = await sessionsApi.create();
      setSessionId(session_id);
      setEvents([]);
      setCurrentState(null);
      setScore(null);
      setSessionEnded(false);
      eventCountRef.current = 0;
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  }, []);

  const emitEvent = useCallback((eventType: string, target?: string) => {
    if (!sessionId || sessionEnded) return;
    const event = {
      event_type: eventType,
      timestamp: Date.now() / 1000,
      page: SHOP_PAGES.find(p => p.id === currentPage)?.path || '/',
      target,
    };
    send(event);
    eventCountRef.current++;
  }, [sessionId, currentPage, send, sessionEnded]);

  const endSession = useCallback(async () => {
    if (!sessionId) return;
    emitEvent('session_end');
    try {
      const result = await sessionsApi.end(sessionId);
      setScore(result);
      setSessionEnded(true);
    } catch (err) {
      console.error('Failed to end session:', err);
    }
  }, [sessionId, emitEvent]);

  const navigateTo = (pageId: string) => {
    setCurrentPage(pageId);
    emitEvent('page_view', pageId);
  };

  const lastMoveRef = useRef(0);
  const handleMouseMove = useCallback(() => {
    const now = Date.now();
    if (now - lastMoveRef.current > 2000) {
      lastMoveRef.current = now;
      emitEvent('mouse_move');
    }
  }, [emitEvent]);

  const handleScroll = useCallback(() => {
    emitEvent('scroll');
  }, [emitEvent]);

  const pageData = SHOP_PAGES.find(p => p.id === currentPage);

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-serif text-3xl font-bold text-warm-text">Behavioral Playground</h1>
          <p className="text-sm text-warm-secondary mt-1">
            Interact with DoppelShop — every action generates behavioral events
          </p>
        </div>
        <div className="flex items-center gap-3">
          {!sessionId ? (
            <button
              onClick={startSession}
              className="px-4 py-2 bg-forest text-white text-xs font-mono font-semibold tracking-wide hover:bg-forest-dark transition-colors"
            >
              START SESSION
            </button>
          ) : !sessionEnded ? (
            <button
              onClick={endSession}
              className="px-4 py-2 bg-accent-red text-white text-xs font-mono font-semibold tracking-wide hover:bg-accent-red/90 transition-colors"
            >
              END SESSION
            </button>
          ) : (
            <button
              onClick={startSession}
              className="px-4 py-2 bg-forest text-white text-xs font-mono font-semibold tracking-wide hover:bg-forest-dark transition-colors"
            >
              NEW SESSION
            </button>
          )}
          {sessionId && (
            <span className="text-[10px] font-mono text-warm-muted">
              Session: {sessionId.slice(0, 8)}... | Events: {events.length}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* DoppelShop Simulation */}
        <div className="lg:col-span-2 space-y-4">
          {/* Shop Navigation */}
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="tag-green">DoppelShop</span>
              <span className="text-[10px] font-mono text-warm-muted">Simulated E-Commerce</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {SHOP_PAGES.slice(0, 5).map(page => (
                <button
                  key={page.id}
                  onClick={() => navigateTo(page.id)}
                  className={`px-3 py-1.5 text-[10px] font-mono font-medium tracking-wide transition-colors ${
                    currentPage === page.id
                      ? 'bg-forest text-white'
                      : 'bg-cream-dark text-warm-secondary hover:text-warm-text'
                  }`}
                >
                  {page.label.toUpperCase()}
                </button>
              ))}
              <span className="text-cream-border self-center mx-1">|</span>
              {SHOP_PAGES.slice(5).map(page => (
                <button
                  key={page.id}
                  onClick={() => navigateTo(page.id)}
                  className={`px-3 py-1.5 text-[10px] font-mono font-medium tracking-wide transition-colors ${
                    currentPage === page.id
                      ? 'bg-forest text-white'
                      : 'bg-cream-dark text-warm-secondary hover:text-warm-text'
                  }`}
                >
                  {page.label.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Shop Content Area */}
          <div
            className="card p-6 min-h-[400px] cursor-pointer select-none"
            onMouseMove={handleMouseMove}
            onScroll={handleScroll}
          >
            {!sessionId ? (
              <div className="flex items-center justify-center h-64 text-warm-muted text-sm">
                Start a session to begin interacting with DoppelShop
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="font-serif text-xl font-bold text-warm-text">{pageData?.label || 'Home'}</h2>
                  <span className="text-[10px] font-mono text-warm-muted">{pageData?.path}</span>
                </div>

                {currentPage === 'home' && (
                  <div className="space-y-4">
                    <div
                      className="p-4 bg-cream-light border border-cream-border cursor-pointer hover:border-forest/30 transition-all"
                      onMouseEnter={() => emitEvent('hover', 'hero_banner')}
                      onClick={() => { emitEvent('mouse_click', 'hero_banner'); navigateTo('products'); }}
                    >
                      <h3 className="font-semibold text-warm-text">Featured Products</h3>
                      <p className="text-sm text-warm-secondary mt-1">Browse our latest collection</p>
                    </div>
                    <div className="grid grid-cols-3 gap-3">
                      {['product1', 'product2', 'product3'].map(pid => {
                        const p = SHOP_PAGES.find(x => x.id === pid)!;
                        return (
                          <div
                            key={pid}
                            className="p-3 bg-white border border-cream-border hover:border-forest/30 cursor-pointer transition-all"
                            onMouseEnter={() => emitEvent('hover', `product_card_${pid}`)}
                            onClick={() => { emitEvent('mouse_click', `product_card_${pid}`); navigateTo(pid); }}
                          >
                            <div className="text-sm text-warm-text">{p.label}</div>
                            <div className="text-xs text-forest font-semibold mt-1">{p.price}</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {(currentPage === 'products' || currentPage.startsWith('product')) && (
                  <div className="space-y-3">
                    {currentPage === 'products' ? (
                      <>
                        <div className="flex gap-2">
                          <input
                            type="text"
                            placeholder="Search products..."
                            className="flex-1 bg-cream border border-cream-border rounded px-3 py-2 text-sm text-warm-text focus:outline-none focus:border-forest"
                            onFocus={() => emitEvent('form_focus', 'search_input')}
                            onKeyDown={() => emitEvent('key_press', 'search_input')}
                          />
                          <button
                            onClick={() => emitEvent('form_submit', 'search_form')}
                            className="px-4 py-2 bg-forest text-white text-sm hover:bg-forest-dark transition-colors"
                          >
                            Search
                          </button>
                        </div>
                        {['product1', 'product2', 'product3'].map(pid => {
                          const p = SHOP_PAGES.find(x => x.id === pid)!;
                          return (
                            <div
                              key={pid}
                              className="p-4 bg-white border border-cream-border hover:border-forest/30 cursor-pointer flex justify-between items-center"
                              onClick={() => { emitEvent('mouse_click', pid); navigateTo(pid); }}
                              onMouseEnter={() => emitEvent('hover', pid)}
                            >
                              <div>
                                <div className="text-sm text-warm-text">{p.label}</div>
                                <div className="text-xs text-warm-muted mt-1">{p.price}</div>
                              </div>
                              <button
                                onClick={(e) => { e.stopPropagation(); emitEvent('mouse_click', 'add_to_cart'); }}
                                className="px-3 py-1 bg-forest/10 text-forest text-xs font-semibold hover:bg-forest/20 transition-colors"
                              >
                                Add to Cart
                              </button>
                            </div>
                          );
                        })}
                      </>
                    ) : (
                      <div className="space-y-3">
                        <h3 className="text-warm-text font-semibold">{pageData?.label}</h3>
                        <p className="text-sm text-warm-secondary">Premium quality product with amazing features.</p>
                        <div className="text-lg font-bold text-forest">{pageData?.price}</div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => emitEvent('mouse_click', 'add_to_cart')}
                            className="px-4 py-2 bg-forest/10 text-forest text-sm font-semibold hover:bg-forest/20 transition-colors"
                          >
                            Add to Cart
                          </button>
                          <button
                            onClick={() => { emitEvent('mouse_click', 'buy_now'); navigateTo('checkout'); }}
                            className="px-4 py-2 bg-forest text-white text-sm hover:bg-forest-dark transition-colors"
                          >
                            Buy Now
                          </button>
                          <button
                            onClick={() => { emitEvent('back_navigation'); navigateTo('products'); }}
                            className="px-4 py-2 bg-cream-dark text-warm-secondary text-sm hover:text-warm-text transition-colors"
                          >
                            Back
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {currentPage === 'login' && (
                  <div className="max-w-sm space-y-3">
                    <input
                      type="text"
                      placeholder="Username"
                      className="w-full bg-cream border border-cream-border rounded px-3 py-2 text-sm text-warm-text focus:outline-none focus:border-forest"
                      onFocus={() => emitEvent('form_focus', 'username_input')}
                      onKeyDown={() => emitEvent('key_press', 'username_input')}
                    />
                    <input
                      type="password"
                      placeholder="Password (simulated — not stored)"
                      className="w-full bg-cream border border-cream-border rounded px-3 py-2 text-sm text-warm-text focus:outline-none focus:border-forest"
                      onFocus={() => emitEvent('form_focus', 'password_input')}
                      onKeyDown={() => emitEvent('key_press', 'password_input')}
                    />
                    <button
                      onClick={() => { emitEvent('form_submit', 'login_form'); emitEvent('successful_action', 'login'); }}
                      className="w-full px-4 py-2 bg-forest text-white text-sm hover:bg-forest-dark transition-colors"
                    >
                      Login (Simulated)
                    </button>
                    <p className="text-xs text-warm-muted">No actual credentials are stored or transmitted.</p>
                  </div>
                )}

                {currentPage === 'cart' && (
                  <div className="space-y-3">
                    <div className="p-3 bg-white border border-cream-border flex justify-between items-center">
                      <span className="text-sm text-warm-text">Sample Item</span>
                      <button
                        onClick={() => emitEvent('mouse_click', 'remove_btn')}
                        className="text-xs text-accent-red hover:underline font-mono"
                      >
                        Remove
                      </button>
                    </div>
                    <button
                      onClick={() => { emitEvent('mouse_click', 'checkout_btn'); navigateTo('checkout'); }}
                      className="px-4 py-2 bg-forest text-white text-sm hover:bg-forest-dark transition-colors"
                    >
                      Proceed to Checkout
                    </button>
                  </div>
                )}

                {currentPage === 'checkout' && (
                  <div className="max-w-sm space-y-3">
                    <input
                      placeholder="Name"
                      className="w-full bg-cream border border-cream-border rounded px-3 py-2 text-sm text-warm-text focus:outline-none focus:border-forest"
                      onFocus={() => emitEvent('form_focus', 'checkout_name')}
                      onKeyDown={() => emitEvent('key_press', 'checkout_name')}
                    />
                    <input
                      placeholder="Address"
                      className="w-full bg-cream border border-cream-border rounded px-3 py-2 text-sm text-warm-text focus:outline-none focus:border-forest"
                      onFocus={() => emitEvent('form_focus', 'checkout_address')}
                      onKeyDown={() => emitEvent('key_press', 'checkout_address')}
                    />
                    <button
                      onClick={() => { emitEvent('form_submit', 'checkout_form'); emitEvent('successful_action', 'checkout'); }}
                      className="w-full px-4 py-2 bg-forest text-white text-sm hover:bg-forest-dark transition-colors"
                    >
                      Place Order (Simulated)
                    </button>
                  </div>
                )}

                {(currentPage === 'search' || currentPage === 'profile') && (
                  <div className="space-y-3">
                    <input
                      placeholder={currentPage === 'search' ? 'Search...' : 'Display Name'}
                      className="w-full bg-cream border border-cream-border rounded px-3 py-2 text-sm text-warm-text focus:outline-none focus:border-forest"
                      onFocus={() => emitEvent('form_focus', `${currentPage}_input`)}
                      onKeyDown={() => emitEvent('key_press', `${currentPage}_input`)}
                    />
                    <button
                      onClick={() => emitEvent('form_submit', `${currentPage}_form`)}
                      className="px-4 py-2 bg-forest text-white text-sm hover:bg-forest-dark transition-colors"
                    >
                      Submit
                    </button>
                  </div>
                )}

                {/* Idle button */}
                <div className="pt-4 border-t border-cream-border">
                  <button
                    onClick={() => emitEvent('idle')}
                    className="text-xs text-warm-muted hover:text-warm-text font-mono"
                  >
                    [Simulate Idle]
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel */}
        <div className="space-y-4">
          {currentState && (
            <div className="card p-4">
              <h3 className="text-[10px] font-mono font-semibold text-warm-text mb-3 tracking-wide uppercase">Product State</h3>
              <div className="space-y-2 font-mono text-[11px]">
                {Object.entries(currentState).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-warm-muted">{key}</span>
                    <span className={`font-semibold ${
                      String(value).includes('SUSPICIOUS') ? 'text-accent-red' :
                      String(value).includes('HUMAN') || String(value).includes('DIVERSE') ? 'text-forest' :
                      'text-forest-light'
                    }`}>
                      {String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {score && (
            <div className="card p-4 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-[10px] font-mono font-semibold text-warm-text tracking-wide uppercase">Final Score</h3>
                <ClassificationBadge classification={score.classification} size="sm" />
              </div>
              <div className="text-3xl font-bold font-mono text-center" style={{
                color: score.automation_score > 70 ? '#C4432B' : score.automation_score > 40 ? '#B87333' : '#2D5A3D'
              }}>
                {score.automation_score}/100
              </div>
              <div className="text-[10px] text-center text-warm-muted font-mono">Behavioral Automation Score</div>
              {score.breakdown && Object.entries(score.breakdown).map(([key, val]) => (
                <ScoreBar key={key} label={key.replace(/_/g, ' ')} value={val as number} />
              ))}
              {score.explanations?.length > 0 && (
                <div className="pt-2 border-t border-cream-border space-y-1">
                  <div className="text-[10px] font-semibold text-warm-text font-mono">Explanations:</div>
                  {score.explanations.map((exp: string, i: number) => (
                    <div key={i} className="text-[10px] text-warm-secondary">&bull; {exp}</div>
                  ))}
                </div>
              )}
            </div>
          )}

          <EventTimeline events={events} maxHeight="400px" />
        </div>
      </div>
    </div>
  );
}
