import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  // Auth is managed client-side via Zustand + localStorage.
  // The httpOnly cookie from the backend (localhost:8000) is cross-origin and
  // is NOT forwarded to Next.js middleware (localhost:3000), so we cannot rely
  // on it here. Page-level useEffect guards handle unauthenticated access.
  return NextResponse.next();
}

export const config = {
  matcher: ['/chat/:path*', '/auth/:path*'],
};
