@echo off
echo Cleaning up unused files from OCR Model 2...

REM Delete unused backend services
del "recircle-cardscan-backend\app\services\vision_ai_service.py"
del "recircle-cardscan-backend\app\services\regex_extractor.py"

REM Delete duplicate router
del "recircle-cardscan-backend\app\routers\pdf_preview.py"

REM Delete unused frontend components
del "frontend\src\components\cards\ExtractedDataCard.tsx"
del "frontend\src\components\table\TableRow.tsx"
del "frontend\src\components\table\TableHeader.tsx"
del "frontend\src\components\table\EmptyState.tsx"
del "frontend\src\pages\NotFound.tsx"
del "frontend\src\utils\formatters.ts"
del "frontend\src\hooks\use-mobile.tsx"

REM Delete unused UI components
del "frontend\src\components\ui\alert.tsx"
del "frontend\src\components\ui\badge.tsx"
del "frontend\src\components\ui\breadcrumb.tsx"
del "frontend\src\components\ui\calendar.tsx"
del "frontend\src\components\ui\carousel.tsx"
del "frontend\src\components\ui\chart.tsx"
del "frontend\src\components\ui\checkbox.tsx"
del "frontend\src\components\ui\command.tsx"
del "frontend\src\components\ui\context-menu.tsx"
del "frontend\src\components\ui\drawer.tsx"
del "frontend\src\components\ui\hover-card.tsx"
del "frontend\src\components\ui\input-otp.tsx"
del "frontend\src\components\ui\menubar.tsx"
del "frontend\src\components\ui\navigation-menu.tsx"
del "frontend\src\components\ui\pagination.tsx"
del "frontend\src\components\ui\popover.tsx"
del "frontend\src\components\ui\resizable.tsx"
del "frontend\src\components\ui\select.tsx"
del "frontend\src\components\ui\sheet.tsx"
del "frontend\src\components\ui\sidebar.tsx"
del "frontend\src\components\ui\slider.tsx"
del "frontend\src\components\ui\sonner.tsx"
del "frontend\src\components\ui\switch.tsx"
del "frontend\src\components\ui\table.tsx"
del "frontend\src\components\ui\textarea.tsx"
del "frontend\src\components\ui\toggle.tsx"
del "frontend\src\components\ui\toggle-group.tsx"
del "frontend\src\components\ui\tooltip.tsx"

echo Cleanup complete! Removed unused files.
pause