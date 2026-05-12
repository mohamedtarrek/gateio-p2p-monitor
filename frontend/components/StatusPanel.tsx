"use client";

/**
 * StatusPanel Component
 * Displays real-time system status: Running/Stopped, last check time,
 * notifications sent, uptime, and current price.
 */

import { SystemStatus } from '@/lib/api';
import { Activity, Clock, Bell, AlertTriangle, TrendingUp, Timer } from 'lucide-react';
import { useEffect, useState } from 'react';

interface StatusPanelProps {
  status: SystemStatus | null;
}

export default function StatusPanel({ status }: StatusPanelProps) {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatDuration = (seconds: number | null): string => {
    if (!seconds) return 'N/A';
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hrs}h ${mins}m ${secs}s`;
  };

  const formatTime = (isoString: string | null): string => {
    if (!isoString) return 'Never';
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      hour12: false 
    });
  };

  const getStatusColor = (status: string | undefined) => {
    switch (status) {
      case 'Running': return 'bg-green-100 text-green-800 border-green-300';
      case 'Stopped': return 'bg-gray-100 text-gray-800 border-gray-300';
      case 'Error': return 'bg-red-100 text-red-800 border-red-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusIcon = (status: string | undefined) => {
    switch (status) {
      case 'Running': return <Activity className="w-4 h-4 text-green-600 animate-pulse" />;
      case 'Stopped': return <Clock className="w-4 h-4 text-gray-600" />;
      case 'Error': return <AlertTriangle className="w-4 h-4 text-red-600" />;
      default: return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Activity className="w-5 h-5 text-primary-600" />
        System Status
      </h2>

      <div className="grid grid-cols-2 gap-4">
        {/* Status Badge */}
        <div className="col-span-2">
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border font-semibold ${getStatusColor(status?.status)}`}>
            {getStatusIcon(status?.status)}
            {status?.status || 'Unknown'}
          </div>
        </div>

        {/* Last Checked */}
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <Clock className="w-4 h-4" />
            <span className="text-sm font-medium">Last Checked</span>
          </div>
          <p className="text-lg font-bold text-gray-800">
            {formatTime(status?.last_checked || null)}
          </p>
        </div>

        {/* Notifications Sent */}
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <Bell className="w-4 h-4" />
            <span className="text-sm font-medium">Notifications</span>
          </div>
          <p className="text-lg font-bold text-gray-800">
            {status?.notifications_sent || 0}
          </p>
        </div>

        {/* Uptime */}
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <Timer className="w-4 h-4" />
            <span className="text-sm font-medium">Uptime</span>
          </div>
          <p className="text-lg font-bold text-gray-800">
            {formatDuration(status?.uptime_seconds || null)}
          </p>
        </div>

        {/* Current Price */}
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm font-medium">Your Price</span>
          </div>
          <p className="text-lg font-bold text-gray-800">
            {status?.last_my_price ? `${status.last_my_price.toFixed(2)} EGP` : 'N/A'}
          </p>
        </div>

        {/* Error Count */}
        {status?.error_count ? (
          <div className="col-span-2 bg-red-50 rounded-lg p-3 border border-red-100">
            <div className="flex items-center gap-2 text-red-600 mb-1">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm font-medium">Errors: {status.error_count}</span>
            </div>
            {status.error_message && (
              <p className="text-sm text-red-700 mt-1">{status.error_message}</p>
            )}
          </div>
        ) : null}
      </div>

      <div className="mt-4 pt-3 border-t border-gray-100 text-xs text-gray-500 flex justify-between">
        <span>Current Time: {currentTime.toLocaleTimeString()}</span>
        <span>Auto-refresh: 5s</span>
      </div>
    </div>
  );
}
