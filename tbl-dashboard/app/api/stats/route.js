import { NextResponse } from 'next/server';
import clientPromise from '@/lib/mongodb';

export async function GET() {
  try {
    const client = await clientPromise;
    const db = client.db('lightning_tracker');
    
    // Get all player stats
    const stats = await db
      .collection('player_stats')
      .find({})
      .toArray();
    
    return NextResponse.json({ stats });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch stats' },
      { status: 500 }
    );
  }
}