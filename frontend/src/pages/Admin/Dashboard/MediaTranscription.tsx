import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { mediaAPI } from '../../../services/api';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/Card';
import { Button } from '../../../components/Button';
import { Input } from '../../../components/Input';

interface TranscriptionResponse {
  success: boolean;
  message: string;
  preview?: string | null;
  tokens_ingested?: number | null;
}

interface HealthResponse {
  groq_api: {
    status: string;
    message: string;
  };
  qdrant: {
    status: string;
    message: string;
    connected: string | boolean;  // Can be string "true"/"false" or boolean
    collections_count?: string | number;
  };
  overall_status: string;
}

export const MediaTranscription: React.FC = () => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Fetch health status
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useQuery<HealthResponse>({
    queryKey: ['media-health'],
    queryFn: mediaAPI.getHealth,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Transcription mutation
  const transcribeMutation = useMutation<TranscriptionResponse, Error, string>({
    mutationFn: (url: string) => mediaAPI.transcribeYouTube(url),
    onSuccess: (data) => {
      setError(null);
      // Refetch health after successful transcription
      refetchHealth();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || err.message || 'Transcription failed');
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!url.trim()) {
      setError('Please paste a YouTube URL');
      return;
    }

    // Basic URL validation
    if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
      setError('Please enter a valid YouTube URL');
      return;
    }

    transcribeMutation.mutate(url.trim());
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ok':
      case 'healthy':
        return 'text-green-600';
      case 'error':
      case 'unhealthy':
        return 'text-red-600';
      case 'degraded':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'ok':
      case 'healthy':
        return 'bg-green-100 text-green-800';
      case 'error':
      case 'unhealthy':
        return 'bg-red-100 text-red-800';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-secondary-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Media Transcription</h1>
          <p className="mt-2 text-sm text-secondary-600">
            Transcribe YouTube videos using Groq Whisper and ingest transcripts into the AI governance corpus.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Transcription Form - Left Column (2/3 width on large screens) */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Transcribe YouTube Video</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label htmlFor="youtube-url" className="block text-sm font-medium text-secondary-700 mb-2">
                      YouTube URL
                    </label>
                    <Input
                      id="youtube-url"
                      type="url"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="https://www.youtube.com/watch?v=..."
                      disabled={transcribeMutation.isPending}
                      className="w-full"
                    />
                    <p className="mt-1 text-xs text-secondary-500">
                      Supports youtube.com and youtu.be URLs
                    </p>
                  </div>

                  <Button
                    type="submit"
                    disabled={transcribeMutation.isPending || !url.trim()}
                    className="w-full"
                  >
                    {transcribeMutation.isPending ? 'Processing...' : 'Transcribe & Ingest'}
                  </Button>
                </form>

                {/* Error Message */}
                {error && (
                  <div className="mt-4 p-3 rounded-md bg-red-50 border border-red-200">
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                )}

                {/* Success Result */}
                {transcribeMutation.data && transcribeMutation.data.success && (
                  <div className="mt-4 space-y-3">
                    <div className="p-3 rounded-md bg-green-50 border border-green-200">
                      <p className="text-sm text-green-700 font-medium">
                        {transcribeMutation.data.message}
                      </p>
                      {transcribeMutation.data.tokens_ingested && (
                        <p className="text-xs text-green-600 mt-1">
                          Approximately {transcribeMutation.data.tokens_ingested.toLocaleString()} tokens ingested
                        </p>
                      )}
                    </div>

                    {transcribeMutation.data.preview && (
                      <div className="p-3 rounded-md bg-white border border-secondary-200">
                        <p className="text-xs font-medium text-secondary-700 mb-2">Transcript Preview:</p>
                        <pre className="text-xs text-secondary-600 whitespace-pre-wrap max-h-64 overflow-auto">
                          {transcribeMutation.data.preview}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Health Check Panel - Right Column (1/3 width on large screens) */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>System Health</CardTitle>
              </CardHeader>
              <CardContent>
                {healthLoading ? (
                  <div className="text-center py-4">
                    <p className="text-sm text-secondary-600">Loading health status...</p>
                  </div>
                ) : health ? (
                  <div className="space-y-4">
                    {/* Overall Status */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-secondary-700">Overall Status</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusBadgeColor(health.overall_status)}`}>
                          {health.overall_status.toUpperCase()}
                        </span>
                      </div>
                    </div>

                    {/* Groq API Status */}
                    <div className="border-t border-secondary-200 pt-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-secondary-700">Groq API</span>
                        <span className={`text-xs font-medium ${getStatusColor(health.groq_api.status)}`}>
                          {health.groq_api.status.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-xs text-secondary-600 mt-1">{health.groq_api.message}</p>
                    </div>

                    {/* Qdrant Status */}
                    <div className="border-t border-secondary-200 pt-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-secondary-700">Qdrant</span>
                        <div className="flex items-center gap-2">
                          <span className={`text-xs font-medium ${getStatusColor(health.qdrant.status)}`}>
                            {health.qdrant.status.toUpperCase()}
                          </span>
                      {(health.qdrant.connected === true || health.qdrant.connected === "true") && (
                        <span className="w-2 h-2 rounded-full bg-green-500" title="Connected" />
                      )}
                        </div>
                      </div>
                      <p className="text-xs text-secondary-600 mt-1">{health.qdrant.message}</p>
                      {health.qdrant.collections_count !== undefined && (
                        <p className="text-xs text-secondary-500 mt-1">
                          {health.qdrant.collections_count} collection(s)
                        </p>
                      )}
                    </div>

                    {/* Refresh Button */}
                    <div className="border-t border-secondary-200 pt-3">
                      <Button
                        onClick={() => refetchHealth()}
                        variant="outline"
                        size="sm"
                        className="w-full"
                      >
                        Refresh Status
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <p className="text-sm text-red-600">Failed to load health status</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

