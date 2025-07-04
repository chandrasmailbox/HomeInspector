import React, { useState } from 'react';
import { Key, ExternalLink, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

interface RoboflowSetupProps {
  onApiKeySubmit: (apiKey: string) => void;
  isConnecting: boolean;
  connectionStatus: 'idle' | 'connecting' | 'connected' | 'error';
  error?: string;
}

const RoboflowSetup: React.FC<RoboflowSetupProps> = ({
  onApiKeySubmit,
  isConnecting,
  connectionStatus,
  error
}) => {
  const [apiKey, setApiKey] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (apiKey.trim()) {
      onApiKeySubmit(apiKey.trim());
    }
  };

  const handleDemoMode = () => {
    onApiKeySubmit('demo');
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="text-center mb-6">
          <div className="bg-blue-100 p-3 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <Key className="h-8 w-8 text-blue-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Connect to Roboflow AI
          </h2>
          <p className="text-gray-600">
            Enter your Roboflow API key to enable professional-grade mold detection
          </p>
        </div>

        {/* Status Messages */}
        {connectionStatus === 'connecting' && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-center space-x-2">
            <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
            <span className="text-blue-700">Connecting to Roboflow...</span>
          </div>
        )}

        {connectionStatus === 'connected' && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-green-700">Successfully connected to Roboflow!</span>
          </div>
        )}

        {connectionStatus === 'error' && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <span className="text-red-700 font-medium">Connection Failed</span>
            </div>
            <p className="text-red-600 text-sm">{error || 'Failed to connect to Roboflow'}</p>
            <p className="text-red-600 text-sm mt-1">
              You can still use the application in demo mode with limited functionality.
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-2">
              Roboflow API Key
            </label>
            <input
              type="password"
              id="apiKey"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your Roboflow API key"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
              disabled={isConnecting}
            />
          </div>

          <div className="flex space-x-4">
            <button
              type="submit"
              disabled={isConnecting || !apiKey.trim()}
              className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isConnecting ? (
                <div className="flex items-center justify-center space-x-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Connecting...</span>
                </div>
              ) : (
                'Connect to Roboflow'
              )}
            </button>

            <button
              type="button"
              onClick={handleDemoMode}
              disabled={isConnecting}
              className="flex-1 bg-gray-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Try Demo Mode
            </button>
          </div>
        </form>

        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-3">How to get your API key:</h3>
          <ol className="text-sm text-gray-600 space-y-2">
            <li className="flex items-start">
              <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded mr-2 mt-0.5">1</span>
              Visit{' '}
              <a
                href="https://app.roboflow.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 mx-1 inline-flex items-center"
              >
                Roboflow <ExternalLink className="h-3 w-3 ml-1" />
              </a>
              and create an account
            </li>
            <li className="flex items-start">
              <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded mr-2 mt-0.5">2</span>
              Go to{' '}
              <a
                href="https://app.roboflow.com/settings/api"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 mx-1 inline-flex items-center"
              >
                Settings → API <ExternalLink className="h-3 w-3 ml-1" />
              </a>
            </li>
            <li className="flex items-start">
              <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded mr-2 mt-0.5">3</span>
              Copy your "Publishable Key\" and paste it above
            </li>
          </ol>
        </div>

        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h4 className="font-medium text-yellow-900 mb-2">Demo Mode Features:</h4>
          <ul className="text-sm text-yellow-800 space-y-1">
            <li>• Computer vision crack and water damage detection</li>
            <li>• Simulated mold detection (for demonstration)</li>
            <li>• Full analysis and reporting features</li>
            <li>• No API key required</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default RoboflowSetup;