#!/usr/bin/env python3
"""
Data Analysis Script for Mesquite Country Club Property Listings
Analyzes the scraped JSON data to summarize realtors and companies by property count.
"""

import json
import os
import re
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional


class PropertyDataAnalyzer:
    """Analyzes property listing data to extract realtor and company statistics"""
    
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.properties = []
        self.load_data()
    
    def load_data(self):
        """Load property data from JSON file"""
        if not os.path.exists(self.json_file_path):
            raise FileNotFoundError(f"JSON file not found: {self.json_file_path}")
        
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            self.properties = json.load(f)
        
        print(f"Loaded {len(self.properties)} properties from {self.json_file_path}")
    
    def parse_courtesy_info(self, courtesy_text: str) -> Tuple[List[str], Optional[str]]:
        """
        Parse courtesy information to extract agent names and company.
        
        Expected formats:
        - "Juan Carlos Nuno / Jesus Martinez, Broker"
        - "John Smith, ABC Realty"
        - "Jane Doe / Bob Johnson, XYZ Company"
        
        Returns:
            Tuple of (agent_names_list, company_name)
        """
        if not courtesy_text or courtesy_text == "Not found":
            return [], None
        
        # Clean up the text
        courtesy_text = courtesy_text.strip()
        
        # Split by comma to separate agents from company
        parts = [part.strip() for part in courtesy_text.split(',')]
        
        if len(parts) >= 2:
            # Agents are before the last comma, company is after
            agents_part = ','.join(parts[:-1]).strip()
            company_part = parts[-1].strip()
        else:
            # Only one part - could be just agents or just company
            agents_part = parts[0].strip()
            company_part = None
        
        # Parse agents (split by '/' or '&' or 'and')
        agent_names = []
        if agents_part:
            # Split by common separators
            agent_separators = [' / ', '/', ' & ', '&', ' and ', ' AND ']
            agents_text = agents_part
            
            for separator in agent_separators:
                if separator in agents_text:
                    agent_names = [name.strip() for name in agents_text.split(separator)]
                    break
            else:
                # No separator found, single agent
                agent_names = [agents_text.strip()]
        
        # Clean agent names (remove titles, extra whitespace)
        cleaned_agents = []
        for agent in agent_names:
            if agent:
                # Remove common titles and suffixes
                agent = re.sub(r'\b(Realtor|REALTOR|Agent|Broker|DRE|BRE)\b.*$', '', agent, flags=re.IGNORECASE)
                agent = agent.strip(' ,.-')
                if agent:
                    cleaned_agents.append(agent)
        
        return cleaned_agents, company_part
    
    def analyze_realtors(self) -> Dict[str, int]:
        """Analyze and count properties by realtor"""
        realtor_counts = Counter()
        
        for prop in self.properties:
            courtesy = prop.get('courtesy_of', '')
            agents, _ = self.parse_courtesy_info(courtesy)
            
            for agent in agents:
                if agent:
                    realtor_counts[agent] += 1
        
        return dict(realtor_counts)
    
    def analyze_companies(self) -> Dict[str, int]:
        """Analyze and count properties by company"""
        company_counts = Counter()
        
        for prop in self.properties:
            courtesy = prop.get('courtesy_of', '')
            _, company = self.parse_courtesy_info(courtesy)
            
            if company:
                company_counts[company] += 1
        
        return dict(company_counts)
    
    def analyze_realtor_company_pairs(self) -> Dict[Tuple[str, str], int]:
        """Analyze realtor-company combinations"""
        pair_counts = Counter()
        
        for prop in self.properties:
            courtesy = prop.get('courtesy_of', '')
            agents, company = self.parse_courtesy_info(courtesy)
            
            for agent in agents:
                if agent and company:
                    pair_counts[(agent, company)] += 1
        
        return dict(pair_counts)
    
    def get_properties_without_courtesy(self) -> List[Dict]:
        """Get properties where courtesy information wasn't found"""
        return [
            prop for prop in self.properties 
            if not prop.get('courtesy_of') or prop.get('courtesy_of') == 'Not found'
        ]
    
    def print_summary_report(self):
        """Print a comprehensive summary report"""
        print("\n" + "="*80)
        print("MESQUITE COUNTRY CLUB PROPERTY LISTINGS ANALYSIS")
        print("="*80)
        
        # Basic stats
        total_properties = len(self.properties)
        properties_without_courtesy = len(self.get_properties_without_courtesy())
        properties_with_courtesy = total_properties - properties_without_courtesy
        
        print(f"\n📊 OVERVIEW")
        print(f"Total Properties: {total_properties}")
        print(f"Properties with Courtesy Info: {properties_with_courtesy}")
        print(f"Properties without Courtesy Info: {properties_without_courtesy}")
        print(f"Success Rate: {properties_with_courtesy/total_properties*100:.1f}%")
        
        # Realtor analysis
        realtor_counts = self.analyze_realtors()
        print(f"\n👥 REALTOR ANALYSIS")
        print(f"Total Unique Realtors: {len(realtor_counts)}")
        
        if realtor_counts:
            print(f"\nTop 10 Realtors by Property Count:")
            print("-" * 50)
            for i, (realtor, count) in enumerate(sorted(realtor_counts.items(), key=lambda x: x[1], reverse=True)[:10], 1):
                print(f"{i:2d}. {realtor:<35} {count:3d} properties")
        
        # Company analysis
        company_counts = self.analyze_companies()
        print(f"\n🏢 COMPANY ANALYSIS")
        print(f"Total Unique Companies: {len(company_counts)}")
        
        if company_counts:
            print(f"\nTop 10 Companies by Property Count:")
            print("-" * 50)
            for i, (company, count) in enumerate(sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:10], 1):
                print(f"{i:2d}. {company:<35} {count:3d} properties")
        
        # Market share analysis
        if realtor_counts:
            total_with_realtors = sum(realtor_counts.values())
            print(f"\n📈 MARKET SHARE (Top 5 Realtors)")
            print("-" * 50)
            for i, (realtor, count) in enumerate(sorted(realtor_counts.items(), key=lambda x: x[1], reverse=True)[:5], 1):
                percentage = count / total_with_realtors * 100
                print(f"{i}. {realtor:<35} {percentage:5.1f}%")
        
        if company_counts:
            total_with_companies = sum(company_counts.values())
            print(f"\n📈 MARKET SHARE (Top 5 Companies)")
            print("-" * 50)
            for i, (company, count) in enumerate(sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5], 1):
                percentage = count / total_with_companies * 100
                print(f"{i}. {company:<35} {percentage:5.1f}%")
        
        # Properties without courtesy info
        if properties_without_courtesy > 0:
            print(f"\n⚠️  PROPERTIES WITHOUT COURTESY INFO")
            print("-" * 50)
            no_courtesy_props = self.get_properties_without_courtesy()
            for i, prop in enumerate(no_courtesy_props[:5], 1):  # Show first 5
                address = prop.get('address', 'Unknown address')
                print(f"{i}. {address}")
            
            if len(no_courtesy_props) > 5:
                print(f"... and {len(no_courtesy_props) - 5} more")
    
    def save_detailed_report(self, output_file: str = "property_analysis_report.txt"):
        """Save a detailed report to a text file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            # Redirect print to file
            import sys
            original_stdout = sys.stdout
            sys.stdout = f
            
            self.print_summary_report()
            
            # Additional detailed sections
            print(f"\n\n📋 DETAILED REALTOR LISTINGS")
            print("="*80)
            realtor_counts = self.analyze_realtors()
            for realtor, count in sorted(realtor_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"{realtor:<40} {count:3d} properties")
            
            print(f"\n\n📋 DETAILED COMPANY LISTINGS")
            print("="*80)
            company_counts = self.analyze_companies()
            for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"{company:<40} {count:3d} properties")
            
            # Restore stdout
            sys.stdout = original_stdout
        
        print(f"\n💾 Detailed report saved to: {output_file}")


def main():
    """Main function to run the analysis"""
    # Look for the JSON file in the current directory
    json_files = [f for f in os.listdir('.') if f.endswith('.json') and 'mesquite' in f.lower()]
    
    if not json_files:
        print("❌ No Mesquite properties JSON file found in current directory.")
        print("Please run the scraper first to generate mesquite_properties.json")
        return
    
    json_file = json_files[0]  # Use the first matching file
    print(f"📁 Using JSON file: {json_file}")
    
    try:
        analyzer = PropertyDataAnalyzer(json_file)
        analyzer.print_summary_report()
        analyzer.save_detailed_report()
        
        print(f"\n✅ Analysis complete!")
        print(f"📊 Summary displayed above")
        print(f"📄 Detailed report saved to: property_analysis_report.txt")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON file: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == '__main__':
    main()