import { ScanMode, ScanResponse, UniverseOption } from "@/types/scanner";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchUniverses(): Promise<UniverseOption[]> {
  const response = await fetch(`${API_BASE_URL}/api/scanner/universes`, {
    cache: "no-store",
  });
  return parseResponse<UniverseOption[]>(response);
}

export async function runScan(universe: string, mode: ScanMode): Promise<ScanResponse> {
  const response = await fetch(`${API_BASE_URL}/api/scanner/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ universe, mode }),
  });
  return parseResponse<ScanResponse>(response);
}

export async function exportScan(universe: string, mode: ScanMode): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/scanner/export`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ universe, mode }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Export failed with status ${response.status}`);
  }
  return response.blob();
}
