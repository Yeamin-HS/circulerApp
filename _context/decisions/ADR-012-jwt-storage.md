# ADR-012: The browser keeps the JWT in memory, mirrored to `sessionStorage`
Status: accepted (provisional, owner to confirm) · 2026-11-17
Context: ARCHITECTURE §10 item 6 left this open. The frontend (Vercel) and backend (Render)
are on different sites. ADR-001 gives a 60-minute JWT and no refresh token.
Options:
- Memory only: safest against theft, but every page refresh signs the user out.
- `localStorage`: survives refresh and browser restart; any injected script can read it,
  and it stays on shared computers.
- Cookie (`HttpOnly`, `SameSite=None`): scripts cannot read it, but cross-site cookies are
  blocked by Safari and increasingly by other browsers, and it needs CSRF protection.
Decision: the token lives in a React state value and is mirrored to `sessionStorage`. It is
sent as `Authorization: Bearer`. The frontend drops it on sign-out, on any 401, and when its
`exp` time passes.
Why: `sessionStorage` survives a refresh but is cleared when the tab closes and is not
shared between tabs, which suits a 60-minute token and shared computers better than
`localStorage`. It works across sites in every browser, unlike cookies. No CSRF protection
is needed because the browser never attaches the token by itself.
Trade-off: a script injected into the page could still read the token (the same exposure as
`localStorage`, for a shorter time). Mitigations: React escapes rendered text; circular text
and LLM output are never inserted as HTML; a Content-Security-Policy header that allows
scripts only from our own origin is added with the Vercel deployment (Increment 4).
Revisit if: frontend and backend move to one site (then use an `HttpOnly` cookie), or a
refresh-token flow is added.
