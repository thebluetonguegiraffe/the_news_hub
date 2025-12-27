import { NextResponse } from 'next/server';
import { API_URL } from '../../config';

const rateLimit = new Map<string, number[]>();

const WINDOW_MS = 60 * 60 * 1000; // 1 hour window

const MAX_REQUESTS = parseInt(process.env.MAX_REQUESTS || '5', 10); // Default to 5 requests per hour if not set
console.log(`[AskHub Config] Rate Limit: ${MAX_REQUESTS} requests/hour`);
console.log(`[AskHub Config] Whitelist: ${process.env.WHITELISTED_IPS || 'None'}`);

const cleanOldRequests = (timestamps: number[]) => {
    const now = Date.now();
    return timestamps.filter(t => now - t < WINDOW_MS);
};

export async function POST(request: Request) {
    try {
        const origin = request.headers.get('origin') || '';
        const referer = request.headers.get('referer') || '';

        // Allow requests only from same origin or empty (server-to-server)
        // Adjust this if you host frontend/backend on different domains
        if (origin && !origin.includes(process.env.NEXT_PUBLIC_APP_URL || 'localhost')) {
        }

        const ip = request.headers.get('x-forwarded-for') || 'unknown-ip';

        // Check Whitelist
        const whitelistedIps = (process.env.WHITELISTED_IPS || '').split(',').map(i => i.trim());
        const isWhitelisted = whitelistedIps.includes(ip) || whitelistedIps.includes('::1') && ip === '127.0.0.1'; // Simple local dev check

        if (isWhitelisted) {
            console.log(`Bypassing rate limit for whitelisted IP: ${ip}`);
        } else {
            let timestamps = rateLimit.get(ip) || [];
            timestamps = cleanOldRequests(timestamps);

            if (timestamps.length >= MAX_REQUESTS) {
                return NextResponse.json(
                    {
                        code: 'RATE_LIMIT',
                        max: MAX_REQUESTS,
                        message: `Rate limit exceeded (${MAX_REQUESTS} requests/hour).`
                    },
                    { status: 429 }
                );
            }

            timestamps.push(Date.now());
            rateLimit.set(ip, timestamps);
        }

        const body = await request.json();

        const apiToken = process.env.NEXT_PUBLIC_API_ACCESS_TOKEN;

        if (!apiToken) {
            console.error("API Token missing on server");
            return NextResponse.json({ error: "Configuration Error: NEXT_PUBLIC_API_ACCESS_TOKEN is missing" }, { status: 500 });
        }

        console.log(`Proxying request to ${API_URL}/ask_hub/`);

        const backendResponse = await fetch(`${API_URL}/ask_hub/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${apiToken}`
            },
            body: JSON.stringify(body),
        });

        if (!backendResponse.ok) {
            const errorText = await backendResponse.text();
            console.error(`Backend error (${backendResponse.status}): ${errorText}`);
            return NextResponse.json(
                { error: `Backend responded with ${backendResponse.status}`, details: errorText },
                { status: backendResponse.status }
            );
        }

        const data = await backendResponse.json();

        return NextResponse.json(data);

    } catch (error: any) {
        console.error("Proxy error:", error);
        return NextResponse.json({
            error: 'Internal Server Error',
            details: error.message,
            stack: error.stack
        }, { status: 500 });
    }
}
