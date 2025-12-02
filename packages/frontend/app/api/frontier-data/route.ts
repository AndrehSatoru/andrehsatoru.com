import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    console.log('[frontier-data] Calling backend with:', {
      url: `${API_BASE_URL}/api/v1/opt/markowitz/frontier-data`,
      body
    });

    const response = await fetch(`${API_BASE_URL}/api/v1/opt/markowitz/frontier-data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[frontier-data] Backend error:', response.status, errorText);
      return NextResponse.json(
        { error: 'Backend error', message: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('[frontier-data] Error:', error);
    return NextResponse.json(
      { error: 'Internal error', message: error.message },
      { status: 500 }
    );
  }
}
