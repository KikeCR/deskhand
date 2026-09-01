import { GithubLogo, LinkedinLogo } from '@phosphor-icons/react'

const GITHUB_URL = 'https://github.com/KikeCR'
const LINKEDIN_URL = 'https://www.linkedin.com/in/luis-enrique-barrantes/'

export function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="border-t border-border py-6 text-muted-foreground">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 sm:flex-row">
        <p className="text-xs">
          &copy; {year} Luis Barrantes. Built with care.
        </p>
        <div className="flex items-center gap-4">
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="GitHub"
            className="transition-colors hover:text-foreground"
          >
            <GithubLogo size={18} weight="regular" />
          </a>
          <a
            href={LINKEDIN_URL}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="LinkedIn"
            className="transition-colors hover:text-foreground"
          >
            <LinkedinLogo size={18} weight="regular" />
          </a>
        </div>
      </div>
    </footer>
  )
}
