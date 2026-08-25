# PowerShell Script to run robot program, capture timing data, and visualize results
# Automated workflow for LEGO robot "eagle"
# Based on roboter.sh pattern: run pybricksdev -> extract JSON -> save to file -> launch visualization

param(
    [string]$RobotName = "eagle",
    [string]$MainScript = "main.py",
    [string]$TimingDataFile = "data\timing_data.json",
    [string]$DiagramScript = "data_analysis\seaborn_diagramm.py"
)

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Robot Automated Timing Workflow" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Robot: $RobotName" -ForegroundColor White
Write-Host "Script: $MainScript" -ForegroundColor White
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if pybricksdev is available
Write-Host "[1/4] Checking pybricksdev..." -ForegroundColor Yellow
try {
    $pybricksdevCheck = Get-Command pybricksdev -ErrorAction Stop
    Write-Host "      ✓ pybricksdev found" -ForegroundColor Green
} catch {
    Write-Host "      ✗ ERROR: pybricksdev not found!" -ForegroundColor Red
    Write-Host "      Install it with: pip install pybricksdev" -ForegroundColor Yellow
    exit 1
}

# Step 2: Run main.py on the robot and capture output
Write-Host ""
Write-Host "[2/4] Running robot program..." -ForegroundColor Yellow
Write-Host "      Connecting to '$RobotName' via Bluetooth..." -ForegroundColor Gray
Write-Host "      This may take a moment..." -ForegroundColor Gray
Write-Host ""

try {
    # Run pybricksdev and capture all output (like roboter.sh does with pipe)
    Write-Host "      ┌─────────────────────────────────────┐" -ForegroundColor DarkGray
    Write-Host "      │      Robot Console Output          │" -ForegroundColor DarkGray
    Write-Host "      └─────────────────────────────────────┘" -ForegroundColor DarkGray
    
    # Capture output in real-time while also storing it
    $outputLines = @()
    $process = Start-Process -FilePath "pybricksdev" -ArgumentList "run","ble",$MainScript `
        -NoNewWindow -PassThru -RedirectStandardOutput "temp_output.txt" -RedirectStandardError "temp_error.txt" -Wait
    
    # Read the captured output
    if (Test-Path "temp_output.txt") {
        $robotOutput = Get-Content "temp_output.txt" -Raw
        Get-Content "temp_output.txt" | ForEach-Object {
            Write-Host "      $_" -ForegroundColor Gray
        }
        Remove-Item "temp_output.txt" -ErrorAction SilentlyContinue
    }
    
    if (Test-Path "temp_error.txt") {
        $errorOutput = Get-Content "temp_error.txt" -Raw
        if ($errorOutput) {
            Get-Content "temp_error.txt" | ForEach-Object {
                if ($_ -and $_ -ne "") {
                    Write-Host "      $_" -ForegroundColor DarkYellow
                }
            }
        }
        Remove-Item "temp_error.txt" -ErrorAction SilentlyContinue
    }
    
    Write-Host ""
    Write-Host "      ✓ Robot program finished!" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "      ✗ ERROR: Failed to run program on robot" -ForegroundColor Red
    Write-Host "      Make sure the robot is turned on and Bluetooth is enabled" -ForegroundColor Yellow
    Write-Host "      Error: $_" -ForegroundColor Red
    
    # Cleanup temp files
    Remove-Item "temp_output.txt" -ErrorAction SilentlyContinue
    Remove-Item "temp_error.txt" -ErrorAction SilentlyContinue
    exit 1
}

# Step 3: Extract and save timing data (like roboter.sh grep/awk pattern)
Write-Host "[3/4] Processing timing data..." -ForegroundColor Yellow

try {
    # Extract JSON data between markers (similar to grep in roboter.sh)
    if ($robotOutput -match "===JSON_START===([\s\S]*?)===JSON_END===") {
        $jsonString = $matches[1].Trim()
        
        Write-Host "      ✓ JSON data extracted" -ForegroundColor Green
        Write-Host "      Data preview: $($jsonString.Substring(0, [Math]::Min(60, $jsonString.Length)))..." -ForegroundColor DarkGray
        
        # Parse the new timing data
        try {
            $newTimingData = $jsonString | ConvertFrom-Json
        } catch {
            Write-Host "      ✗ ERROR: Invalid JSON format" -ForegroundColor Red
            Write-Host "      JSON content: $jsonString" -ForegroundColor DarkGray
            exit 1
        }
        
        # Load existing timing_data.json or create new array
        if (Test-Path $TimingDataFile) {
            try {
                $existingData = Get-Content $TimingDataFile -Raw | ConvertFrom-Json
                
                # Ensure it's an array
                if ($existingData -isnot [array]) {
                    $existingData = @($existingData)
                }
                
                # Filter out empty objects
                $existingData = @($existingData | Where-Object { 
                    $_.PSObject.Properties.Count -gt 0 
                })
            } catch {
                Write-Host "      ! Warning: Existing $TimingDataFile is corrupted, creating new one" -ForegroundColor Yellow
                $existingData = @()
            }
        } else {
            Write-Host "      Creating new $TimingDataFile" -ForegroundColor Gray
            $existingData = @()
        }
        
        # Add new run data to array
        $existingData += $newTimingData
        
        # Save updated data with proper formatting
        $jsonOutput = $existingData | ConvertTo-Json -Depth 10
        $jsonOutput | Out-File -FilePath $TimingDataFile -Encoding UTF8 -NoNewline
        
        Write-Host "      ✓ Data saved to: $TimingDataFile" -ForegroundColor Green
        Write-Host "      ✓ Total runs recorded: $($existingData.Count)" -ForegroundColor Cyan
        
    } else {
        Write-Host "      ! WARNING: No timing data found in output" -ForegroundColor Yellow
        Write-Host "      The robot may not have pressed the LEFT button to save data" -ForegroundColor Yellow
        Write-Host "      Or the program may have been interrupted" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "      Skipping diagram generation..." -ForegroundColor Yellow
        exit 0
    }

    # Extract heading data
    if ($robotOutput -match "===HEADING_START===([\s\S]*?)===HEADING_END===") {
        $headingJson = $matches[1].Trim()
        Write-Host "      ✓ Heading data extracted" -ForegroundColor Green
        
        $headingFile = "data\heading_data.json"
        if (Test-Path $headingFile) {
            try {
                $existingHeading = Get-Content $headingFile -Raw | ConvertFrom-Json
                if ($existingHeading -isnot [array]) {
                    $existingHeading = @($existingHeading)
                }
            } catch {
                $existingHeading = @()
            }
        } else {
            $existingHeading = @()
        }

        # Parse new heading data (array of entries) and wrap as one run
        try {
            $newHeading = $headingJson | ConvertFrom-Json
            $runEntry = @{
                "run" = $existingData.Count
                "segments" = $newHeading
            }
            $existingHeading += $runEntry
            $existingHeading | ConvertTo-Json -Depth 10 | Out-File -FilePath $headingFile -Encoding UTF8 -NoNewline
            Write-Host "      ✓ Heading data saved to: $headingFile" -ForegroundColor Green
        } catch {
            Write-Host "      ! Warning: Could not parse heading data" -ForegroundColor Yellow
        }
    } else {
        Write-Host "      ! No heading data found (older robot code?)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "      ✗ ERROR: Failed to process timing data" -ForegroundColor Red
    Write-Host "      Error: $_" -ForegroundColor Red
    Write-Host "      Stack: $($_.ScriptStackTrace)" -ForegroundColor DarkGray
    exit 1
}

# Step 4: Launch timing diagram program (like roboter.sh running plotter.py)
Write-Host ""
Write-Host "[4/4] Launching visualization..." -ForegroundColor Yellow

try {
    if (Test-Path $DiagramScript) {
        Write-Host "      Starting $DiagramScript..." -ForegroundColor Gray
        Write-Host ""
        Write-Host "====================================" -ForegroundColor Cyan
        Write-Host ""
        
        # Run the diagram script (like roboter.sh does with python plotter.py)
        python $DiagramScript
        
        Write-Host ""
        Write-Host "====================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "✓ Workflow completed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Summary:" -ForegroundColor Cyan
        Write-Host "  • Robot program executed" -ForegroundColor White
        Write-Host "  • Timing data saved to $TimingDataFile" -ForegroundColor White
        Write-Host "  • Diagrams generated" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "      ! WARNING: $DiagramScript not found" -ForegroundColor Yellow
        Write-Host "      Data saved but visualization skipped" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "✓ Data collection completed!" -ForegroundColor Green
        Write-Host "  Timing data saved to: $TimingDataFile" -ForegroundColor White
    }
} catch {
    Write-Host "      ✗ ERROR: Failed to launch visualization" -ForegroundColor Red
    Write-Host "      Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "! Partial success: Data was saved to $TimingDataFile" -ForegroundColor Yellow
    Write-Host "  You can manually run: python $DiagramScript" -ForegroundColor Gray
}

