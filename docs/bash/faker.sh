#!/bin/bash

# ============================================================
# Faker Script for Fitness Freaks Gym Management App
# Generates fake data for testing and development
# ============================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}🏋️  FITNESS FREAKS - FAKE DATA GENERATOR${NC}"
echo -e "${BLUE}============================================================${NC}"

# Change to project root
cd "$PROJECT_ROOT"

# Check if virtual environment exists and activate
if [ -d "venv" ]; then
    echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Check if Faker is installed
echo -e "${YELLOW}🔍 Checking dependencies...${NC}"
python -c "import faker" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}📥 Installing Faker...${NC}"
    pip install Faker
fi

# Parse arguments
CLEAR_FLAG=""
if [ "$1" == "--clear" ] || [ "$1" == "-c" ]; then
    echo -e "${RED}⚠️  Will clear existing data before generating new data${NC}"
    CLEAR_FLAG="--clear"
fi

# Run the faker script
echo -e "${GREEN}🚀 Running faker script...${NC}"
echo ""

python "$SCRIPT_DIR/generate_fake_data.py" $CLEAR_FLAG

# Check if successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Fake data generation completed successfully!${NC}"
else
    echo -e "${RED}❌ Error generating fake data${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${YELLOW}💡 Tips:${NC}"
echo -e "   • Run with ${GREEN}--clear${NC} to delete existing data first"
echo -e "   • Default password for all users: ${GREEN}password123${NC}"
echo -e "   • Access dashboard: ${GREEN}http://127.0.0.1:8000/dashboard/${NC}"
echo -e "${BLUE}============================================================${NC}"

