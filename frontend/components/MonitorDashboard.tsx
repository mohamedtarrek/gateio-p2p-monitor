"use client";

/**
 * MonitorDashboard Component
 * Main orchestration component that combines all sub-components
 * and handles polling for status updates.
 */

import { useState, useEffect, useCallback } from 'react';
import { api, MonitorSettings, SystemStatus, NotificationLog as NotificationLogType } from '@/lib/api';
import SettingsForm from './SettingsForm';
import StatusPanel from './StatusPanel';
import NotificationLog from './NotificationLog';
import { Play, Square, RefreshCw, Loader2, Shield } from 'lucide-react';

export default function MonitorDashboard() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [settings, setSettings] = useState<MonitorSettings | null>(null);
  const [notifications, setNotifications] = useState<NotificationLogType[]>([]);
  const [totalNotifications, setTotalNotifications] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [isStopping, setIsStopping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch status from backend
  const fetchStatus = useCallback(async () => {
    try {
      const data = await api.getStatus();
      setStatus(data);
      setSettings(data.current_settings);
      setError(null);
    } catch (err: any) {
      setError('Failed to connect to backend. Is the server running?');
    }
  }, []);

  // Fetch notification history
  const fetchHistory = useCallback(async () => {
    try {
      const data = await api.getHistory(50);
      setNotifications(data.notifications);
      setTotalNotifications(data.total);
    } catch (err) {
      // Silently fail - history is not critical
    }
  }, []);

  // Initial load and polling
  useEffect(() => {
    fetchStatus();
    fetchHistory();

    const interval = setInterval(() => {
      fetchStatus();
      fetchHistory();
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, [fetchStatus, fetchHistory]);

  const handleStart = async () => {
    setIsStarting(true);
    setError(null);
    try {
      await api.startMonitor();
      await fetchStatus();
    } catch (err: any) {
      setError(err.message || 'Failed to start monitor');
    } finally {
      setIsStarting(false);
    }
  };

  const handleStop = async () => {
    setIsStopping(true);
    setError(null);
    try {
      await api.stopMonitor();
      await fetchStatus();
    } catch (err: any) {
      setError(err.message || 'Failed to stop monitor');
    } finally {
      setIsStopping(false);
    }
  };

  const handleSettingsSaved = (newSettings: MonitorSettings) => {
    setSettings(newSettings);
  };

  const handleClearHistory = async () => {
    try {
      await api.clearHistory();
      setNotifications([]);
      setTotalNotifications(0);
    } catch (err) {
      setError('Failed to clear history');
    }
  };

  const isRunning = status?.status === 'Running';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-primary-600 p-2 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Gate.io P2P Monitor</h1>
                <p className="text-sm text-gray-500">USDT/EGP Price Tracking with Telegram Alerts</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                isRunning 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                <span className={`w-2 h-2 rounded-full mr-2 ${isRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
                {status?.status || 'Loading...'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3 text-red-700">
            <RefreshCw className="w-5 h-5" />
            {error}
          </div>
        )}

        {/* Control Bar */}
        <div className="mb-6 flex gap-3">
          <button
            onClick={handleStart}
            disabled={isStarting || isRunning}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
              isRunning
                ? 'bg-green-100 text-green-700 cursor-default'
                : 'bg-green-600 hover:bg-green-700 text-white shadow-md hover:shadow-lg'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isStarting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
            {isRunning ? 'Running' : isStarting ? 'Starting...' : 'Start Monitoring'}
          </button>

          <button
            onClick={handleStop}
            disabled={isStopping || !isRunning}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
              !isRunning
                ? 'bg-gray-100 text-gray-500 cursor-default'
                : 'bg-red-600 hover:bg-red-700 text-white shadow-md hover:shadow-lg'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isStopping ? <Loader2 className="w-5 h-5 animate-spin" /> : <Square className="w-5 h-5" />}
            {isStopping ? 'Stopping...' : 'Stop Monitoring'}
          </button>

          <button
            onClick={() => { fetchStatus(); fetchHistory(); }}
            className="flex items-center gap-2 px-4 py-3 rounded-lg font-medium bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-6">
            <SettingsForm 
              onSettingsSaved={handleSettingsSaved} 
              currentSettings={settings} 
            />
            <StatusPanel status={status} />
          </div>

          {/* Right Column */}
          <div>
            <NotificationLog 
              notifications={notifications} 
              total={totalNotifications}
              onClear={handleClearHistory}
            />
          </div>
        </div>

        {/* Info Footer */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">How it works</h3>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>Enter your Gate.io trader name and configure Telegram credentials</li>
            <li>Set minimum quantity to filter out small-volume competitors</li>
            <li>Click "Start Monitoring" to begin automatic price checks</li>
            <li>Receive Telegram alerts when competitors list higher prices than yours</li>
            <li>Duplicate notifications are prevented for the same price level</li>
          </ul>
        </div>
      </main>
    </div>
  );
}
