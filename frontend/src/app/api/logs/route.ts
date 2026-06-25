import { NextRequest, NextResponse } from "next/server";
import { getProjects } from "@/lib/api/project";

export async function GET(request: NextRequest) {
  // Use telemetry token for the actual logs API call
  const telemetryToken = process.env.TELEMETRY_API_TOKEN;
  if (!telemetryToken) {
    return NextResponse.json(
      { error: "API token not configured" },
      { status: 500 },
    );
  }
  // Get project_id from request params
  const searchParams = request.nextUrl.searchParams;
  const projectId = searchParams.get("project_id");
  if (!projectId) {
    return NextResponse.json({ error: "Missing project_id" }, { status: 400 });
  }

  // MVP Bypass: Skipping PropelAuth validation and project access check
  // Fetch logs from telemetry API
  try {
    const url = `${process.env.TELEMETRY_API_URL}/v1/telemetry/logs?${searchParams.toString()}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${telemetryToken}`,
      },
    });
    if (!response.ok) {
      throw new Error(
        `Failed to fetch logs: ${response.status} ${response.statusText}`,
      );
    }
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching logs:", error);
    return NextResponse.json(
      { error: "Next.js Server Error" + (error as Error).message },
      { status: 500 },
    );
  }
}
