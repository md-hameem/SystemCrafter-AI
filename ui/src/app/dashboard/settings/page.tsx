'use client'

import { useAuthStore } from '@/lib/store'
import { Card, CardContent, CardHeader, Button, Input } from '@/components/ui'
import { User, Shield, Bell } from 'lucide-react'

export default function SettingsPage() {
  const user = useAuthStore((state) => state.user)

  return (
    <div className="p-6 lg:p-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-slate-400">Manage your account and preferences</p>
      </div>

      <div className="space-y-6">
        {/* Profile Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <User className="h-5 w-5 text-primary-500" />
              <h2 className="text-lg font-semibold text-white">Profile</h2>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center text-2xl text-white font-medium">
                {user?.full_name?.[0] || user?.email[0].toUpperCase()}
              </div>
              <div>
                <p className="text-lg font-medium text-white">
                  {user?.full_name || 'User'}
                </p>
                <p className="text-slate-400">{user?.email}</p>
              </div>
            </div>
            
            <div className="grid sm:grid-cols-2 gap-4 pt-4">
              <Input
                label="Full Name"
                defaultValue={user?.full_name || ''}
                placeholder="Your name"
              />
              <Input
                label="Email"
                type="email"
                defaultValue={user?.email}
                disabled
              />
            </div>
            
            <Button>Save Changes</Button>
          </CardContent>
        </Card>

        {/* Security Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary-500" />
              <h2 className="text-lg font-semibold text-white">Security</h2>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid sm:grid-cols-2 gap-4">
              <Input
                label="Current Password"
                type="password"
                placeholder="••••••••"
              />
              <div />
              <Input
                label="New Password"
                type="password"
                placeholder="••••••••"
              />
              <Input
                label="Confirm New Password"
                type="password"
                placeholder="••••••••"
              />
            </div>
            
            <Button>Update Password</Button>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-primary-500" />
              <h2 className="text-lg font-semibold text-white">Notifications</h2>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <label className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-white">Email Notifications</p>
                  <p className="text-sm text-slate-400">
                    Receive email updates about your projects
                  </p>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="w-5 h-5 rounded border-slate-600 bg-slate-700 text-primary-600 focus:ring-primary-500"
                />
              </label>
              
              <label className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-white">Generation Complete</p>
                  <p className="text-sm text-slate-400">
                    Get notified when code generation finishes
                  </p>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="w-5 h-5 rounded border-slate-600 bg-slate-700 text-primary-600 focus:ring-primary-500"
                />
              </label>
              
              <label className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-white">Weekly Summary</p>
                  <p className="text-sm text-slate-400">
                    Receive a weekly summary of your activity
                  </p>
                </div>
                <input
                  type="checkbox"
                  className="w-5 h-5 rounded border-slate-600 bg-slate-700 text-primary-600 focus:ring-primary-500"
                />
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Danger Zone */}
        <Card className="border-red-900/50">
          <CardHeader>
            <h2 className="text-lg font-semibold text-red-400">Danger Zone</h2>
          </CardHeader>
          <CardContent>
            <p className="text-slate-400 mb-4">
              Once you delete your account, there is no going back. Please be certain.
            </p>
            <Button variant="danger">Delete Account</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
