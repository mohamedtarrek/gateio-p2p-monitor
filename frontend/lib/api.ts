/**
 * API client for Gate.io P2P Monitor backend.
 * Handles all HTTP requests to the FastAPI server.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface MonitorSettings {
  trader_name: string;
  min_quantity: number;
  telegram_bot_token: string;
  telegram_chat_id: string;
  polling_interval: number;
  payment_method: string;
}

export interface SystemStatus {
  status: 'Running' | 'Stopped' | 'Error';
  last_checked: string | null;
  notifications_sent: number;
  current_settings: MonitorSettings | null;
  error_message: string | null;
  uptime_seconds: number | null;
  error_count: number;
  last_my_price: number | null;
}

export interface NotificationLog {
  id: string;
  payload: {
    competitor_name: string;
    competitor_price: number;
    my_price: number;
    price_difference: number;
    max_quantity: number;
    ad_link: string;
    timestamp: string;
    payment_method: string;
  };
  sent_at: string;
  telegram_message_id: number;
  status: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE;
  }

  private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async updateSettings(settings: MonitorSettings): Promise<{ success: boolean; message: string; error?: string }> {
    return this.fetch('/api/settings', {
      method: 'POST',
      body: JSON.stringify(settings),
    });
  }

  async getStatus(): Promise<SystemStatus> {
    return this.fetch('/api/status');
  }

  async startMonitor(): Promise<{ success: boolean; message: string }> {
    return this.fetch('/api/start', { method: 'POST' });
  }

  async stopMonitor(): Promise<{ success: boolean; message: string }> {
    return this.fetch('/api/stop', { method: 'POST' });
  }

  async testTelegram(settings: MonitorSettings): Promise<{ success: boolean; message: string }> {
    return this.fetch('/api/test-telegram', {
      method: 'POST',
      body: JSON.stringify(settings),
    });
  }

  async getHistory(limit: number = 50): Promise<{ notifications: NotificationLog[]; total: number }> {
    return this.fetch(`/api/history?limit=${limit}`);
  }

  async clearHistory(): Promise<{ success: boolean; message: string }> {
    return this.fetch('/api/history', { method: 'DELETE' });
  }
}

export const api = new ApiClient();
