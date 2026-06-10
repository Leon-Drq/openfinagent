import { SiteNav } from "@/components/site/site-nav"
import { SiteHero } from "@/components/site/site-hero"
import { SitePlatform } from "@/components/site/site-platform"
import { SiteProviders } from "@/components/site/site-providers"
import { SiteWhy } from "@/components/site/site-why"
import { SiteArchitecture } from "@/components/site/site-architecture"
import { SiteFeatures } from "@/components/site/site-features"
import { SiteQuickstart } from "@/components/site/site-quickstart"
import { SiteCompare } from "@/components/site/site-compare"
import { SiteRoadmap } from "@/components/site/site-roadmap"
import { SiteCTA } from "@/components/site/site-cta"
import { SiteFooter } from "@/components/site/site-footer"

export default function Page() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <SiteNav />
      <SiteHero />
      <SitePlatform />
      <SiteProviders />
      <SiteWhy />
      <SiteArchitecture />
      <SiteFeatures />
      <SiteQuickstart />
      <SiteCompare />
      <SiteRoadmap />
      <SiteCTA />
      <SiteFooter />
    </main>
  )
}
