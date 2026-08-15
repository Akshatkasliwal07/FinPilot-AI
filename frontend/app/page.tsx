import Navbar from "@/components/layout/Navbar";
import Hero from "@/components/landing/Hero";
import Features from "@/components/landing/Features";
import Testimonials from "@/components/landing/Testimonials";
import Pricing from "@/components/landing/Pricing";
import BentoFeatures from "@/components/landing/BentoFeatures";
import Timeline from "@/components/landing/Timeline";
import MarketTicker from "@/components/landing/MarketTicker";
export default function Home() {
  return (
    <>
      <Navbar />
      <Hero />
      <MarketTicker />
      <Features />
      <Testimonials />
      <Pricing />
      <BentoFeatures />
      <Timeline />
    </>
  );
}