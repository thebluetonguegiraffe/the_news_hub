import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {

  // PWD auth disabled

  // const authCookie = request.cookies.get('authenticated');

  // const isLoginPage = request.nextUrl.pathname === '/login';
  // if (!authCookie && !isLoginPage) {
  //   return NextResponse.redirect(new URL('/login', request.url));
  // }

  // if (authCookie && isLoginPage) {
  //   return NextResponse.redirect(new URL('/', request.url));
  // }

  return NextResponse.next();
}
