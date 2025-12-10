import Link from 'next/link'
import { ArrowRight, Sparkles, Code, Zap, Shield } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-slate-900/80 backdrop-blur-md border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Sparkles className="h-8 w-8 text-primary-500" />
              <span className="text-xl font-bold text-white">SystemCrafter AI</span>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/login"
                className="text-slate-300 hover:text-white transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-primary-900/50 text-primary-400 px-4 py-2 rounded-full text-sm font-medium mb-8">
            <Sparkles className="h-4 w-4" />
            <span>AI-Powered Architecture Generator</span>
          </div>
          
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
            Describe Your Product,
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-cyan-400">
              Get Production Code
            </span>
          </h1>
          
          <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10">
            Transform natural language product descriptions into complete, production-ready 
            full-stack applications with architecture diagrams, APIs, databases, and deployment configs.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/register"
              className="inline-flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all hover:scale-105"
            >
              Start Building Free
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              href="#demo"
              className="inline-flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all border border-slate-600"
            >
              Watch Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Everything You Need to Ship Fast
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Code className="h-8 w-8" />}
              title="Full-Stack Generation"
              description="FastAPI backend, Next.js frontend, PostgreSQL database - all generated from your description."
            />
            <FeatureCard
              icon={<Zap className="h-8 w-8" />}
              title="One-Click Deploy"
              description="Docker Compose for local dev, Kubernetes manifests for production. Deploy in minutes."
            />
            <FeatureCard
              icon={<Shield className="h-8 w-8" />}
              title="Production Ready"
              description="Authentication, API validation, error handling, logging - all built-in from the start."
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 bg-slate-800/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            How It Works
          </h2>
          
          <div className="space-y-8">
            <StepCard
              number="1"
              title="Describe Your Product"
              description="Write a natural language description of your application. Be as detailed as you want."
            />
            <StepCard
              number="2"
              title="AI Generates Architecture"
              description="Our AI agents analyze your requirements and generate optimal architecture, APIs, and database schema."
            />
            <StepCard
              number="3"
              title="Get Production Code"
              description="Download your complete project with backend, frontend, infrastructure configs, and deployment scripts."
            />
            <StepCard
              number="4"
              title="Deploy & Iterate"
              description="Run locally with docker-compose, deploy to cloud, and iterate with AI-assisted modifications."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Build Your Next Project?
          </h2>
          <p className="text-xl text-slate-400 mb-8">
            Join thousands of developers shipping faster with SystemCrafter AI.
          </p>
          <Link
            href="/register"
            className="inline-flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all hover:scale-105"
          >
            Get Started for Free
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-700 py-12 px-4">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary-500" />
            <span className="text-lg font-bold text-white">SystemCrafter AI</span>
          </div>
          <p className="text-slate-400 text-sm">
            © {new Date().getFullYear()} SystemCrafter AI. All rights reserved.
          </p>
        </div>
      </footer>
    </main>
  )
}

function FeatureCard({ icon, title, description }: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 hover:border-primary-500/50 transition-colors">
      <div className="text-primary-500 mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-slate-400">{description}</p>
    </div>
  )
}

function StepCard({ number, title, description }: {
  number: string
  title: string
  description: string
}) {
  return (
    <div className="flex gap-6 items-start">
      <div className="flex-shrink-0 w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
        {number}
      </div>
      <div>
        <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
        <p className="text-slate-400">{description}</p>
      </div>
    </div>
  )
}
