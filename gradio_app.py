"""
Alfalfa Cell Segmentation Analysis - Gradio Web Interface

A user-friendly web interface for biologists to analyze alfalfa stem cross-sections
using AI-powered segmentation and chemical composition analysis.

Features:
- Upload microscopy images (.nd2, .tiff, .jpg)
- AI-powered cell segmentation (YOLO)
- Lignin and Pectin detection
- Download results and visualizations
- No coding required!

Usage:
    python gradio_app.py
    # Opens web interface at http://localhost:7860
"""

import gradio as gr
import sys
from pathlib import Path

# Add project root to path for imports
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

# Import backend modules
from src.gradio_ui.backend.image_processor import ImageProcessor
from src.gradio_ui.backend.segmentation import SegmentationEngine
from src.gradio_ui.backend.chemical_analysis import ChemicalAnalyzer
from src.gradio_ui.backend.results_manager import ResultsManager
from src.gradio_ui.config import UIConfig

# Initialize configuration
config = UIConfig()

# Initialize backend engines
image_processor = ImageProcessor(config)
segmentation_engine = SegmentationEngine(config)
chemical_analyzer = ChemicalAnalyzer(config)
results_manager = ResultsManager(config)


def create_upload_tab():
    """Tab 1: Upload and Process Images"""
    with gr.Tab("📤 Upload & Process"):
        gr.Markdown("""
        ## Upload Microscopy Images
        
        Upload your alfalfa stem cross-section images in any format:
        - `.nd2` (Nikon microscopy format)
        - `.tiff` / `.tif` (TIFF images)
        - `.jpg` / `.jpeg` / `.png` (Standard images)
        
        The system will automatically convert them to the required format.
        """)
        
        with gr.Row():
            with gr.Column():
                # File upload component
                file_upload = gr.Files(
                    label="Upload Images",
                    file_types=[".nd2", ".tiff", ".tif", ".jpg", ".jpeg", ".png"],
                    type="filepath"
                )
                
                # Processing button
                process_btn = gr.Button("🔄 Convert Images", variant="primary", size="lg")
                
            with gr.Column():
                # Status output
                status_text = gr.Textbox(
                    label="Status",
                    lines=10,
                    interactive=False,
                    placeholder="Upload images and click 'Convert Images' to start..."
                )
                
        # Converted images gallery
        gr.Markdown("### Converted Images")
        converted_gallery = gr.Gallery(
            label="Processed Images",
            columns=4,
            height="auto"
        )
        
        # Wire up processing
        process_btn.click(
            fn=image_processor.process_uploads,
            inputs=[file_upload],
            outputs=[status_text, converted_gallery]
        )
        
        return file_upload, converted_gallery


def create_segmentation_tab():
    """Tab 2: AI Segmentation"""
    with gr.Tab("🔬 Segmentation"):
        gr.Markdown("""
        ## AI-Powered Cell Segmentation
        
        Run the trained YOLO model to detect and segment cell walls in your images.
        The model will:
        - Detect individual cells
        - Create segmentation masks
        - Remove background
        - Generate visualization overlays
        """)
        
        with gr.Row():
            with gr.Column():
                # Image selector
                image_selector = gr.Dropdown(
                    label="Select Image to Analyze",
                    choices=[],
                    interactive=True
                )
                
                # Confidence threshold slider
                confidence_slider = gr.Slider(
                    minimum=0.1,
                    maximum=0.9,
                    value=0.25,
                    step=0.05,
                    label="Confidence Threshold",
                    info="Lower = more detections, Higher = more confident detections"
                )
                
                # Run segmentation button
                segment_btn = gr.Button("🎯 Run Segmentation", variant="primary", size="lg")
                
            with gr.Column():
                # Segmentation results
                seg_status = gr.Textbox(
                    label="Segmentation Status",
                    lines=5,
                    interactive=False
                )
                
        # Results display
        with gr.Row():
            # Original image
            original_img = gr.Image(
                label="Original Image",
                type="filepath"
            )
            
            # Segmented image
            segmented_img = gr.Image(
                label="Segmented Result",
                type="filepath"
            )
            
        # Background removed image
        gr.Markdown("### Background Removed (for chemical analysis)")
        bg_removed_img = gr.Image(
            label="Background Removed",
            type="filepath"
        )
        
        # Wire up segmentation
        segment_btn.click(
            fn=segmentation_engine.run_segmentation,
            inputs=[image_selector, confidence_slider],
            outputs=[seg_status, original_img, segmented_img, bg_removed_img]
        )
        
        return image_selector, segmented_img, bg_removed_img


def create_chemical_analysis_tab():
    """Tab 3: Chemical Composition Analysis"""
    with gr.Tab("🧪 Chemical Analysis"):
        gr.Markdown("""
        ## Lignin & Pectin Detection

        Analyze the chemical composition of segmented cells:
        - **Lignin Detection**: Identifies red-stained regions (PG staining)
        - **Pectin Detection**: Identifies burgundy regions (Ruthenium Red staining)

        Results include pixel counts, ratios, and area measurements in microns.
        """)

        with gr.Row():
            with gr.Column():
                # Analysis type selector
                analysis_type = gr.CheckboxGroup(
                    choices=["Lignin (PG)", "Pectin (RR)"],
                    value=["Lignin (PG)", "Pectin (RR)"],
                    label="Analysis Type",
                    info="Select which analyses to run"
                )

                # Image selector for analysis
                chem_image_selector = gr.Dropdown(
                    label="Select Background-Removed Image",
                    choices=[],
                    interactive=True
                )

                # Run analysis button
                analyze_btn = gr.Button("🔬 Run Chemical Analysis", variant="primary", size="lg")

            with gr.Column():
                # Analysis status
                chem_status = gr.Textbox(
                    label="Analysis Status",
                    lines=8,
                    interactive=False
                )

        # Results visualization
        with gr.Row():
            # Lignin visualization
            lignin_viz = gr.Image(
                label="Lignin Detection Overlay",
                type="filepath"
            )

            # Pectin visualization
            pectin_viz = gr.Image(
                label="Pectin Detection Overlay",
                type="filepath"
            )

        # Numerical results
        gr.Markdown("### Quantitative Results")
        results_table = gr.Dataframe(
            label="Chemical Composition Data",
            headers=["Metric", "Lignin", "Pectin"],
            interactive=False
        )

        # Wire up chemical analysis
        analyze_btn.click(
            fn=chemical_analyzer.run_analysis,
            inputs=[chem_image_selector, analysis_type],
            outputs=[chem_status, lignin_viz, pectin_viz, results_table]
        )

        return chem_image_selector, results_table


def create_results_tab():
    """Tab 4: Results & Export"""
    with gr.Tab("📊 Results & Export"):
        gr.Markdown("""
        ## View Results and Download Data

        Browse all analysis results and download reports.
        """)

        with gr.Row():
            with gr.Column():
                # Session results browser
                gr.Markdown("### Current Session Results")
                session_summary = gr.Textbox(
                    label="Session Summary",
                    lines=15,
                    interactive=False
                )

                # Refresh button
                refresh_btn = gr.Button("🔄 Refresh Results", size="sm")

            with gr.Column():
                # Download options
                gr.Markdown("### Download Options")

                download_format = gr.Radio(
                    choices=["CSV", "Excel", "ZIP (All Files)"],
                    value="CSV",
                    label="Export Format"
                )

                export_btn = gr.Button("📥 Download Results", variant="primary")

                # Download link
                download_file = gr.File(
                    label="Download Ready",
                    interactive=False
                )

        # Results visualization gallery
        gr.Markdown("### All Visualizations")
        results_gallery = gr.Gallery(
            label="Analysis Results Gallery",
            columns=3,
            height="auto"
        )

        # Wire up results display
        refresh_btn.click(
            fn=results_manager.get_session_summary,
            inputs=[],
            outputs=[session_summary, results_gallery]
        )

        export_btn.click(
            fn=results_manager.export_results,
            inputs=[download_format],
            outputs=[download_file]
        )

        return session_summary, results_gallery


def create_settings_tab():
    """Tab 5: Settings & Configuration"""
    with gr.Tab("⚙️ Settings"):
        gr.Markdown("""
        ## Model and Analysis Settings

        Configure the AI model and analysis parameters.
        """)

        with gr.Row():
            with gr.Column():
                gr.Markdown("### YOLO Model Settings")

                model_path = gr.Textbox(
                    label="Model Path",
                    value=str(config.model_path),
                    interactive=True,
                    info="Path to trained YOLO model (best.pt)"
                )

                model_status = gr.Textbox(
                    label="Model Status",
                    value="",
                    interactive=False,
                    lines=3
                )

                check_model_btn = gr.Button("🔍 Check Model", size="sm")

            with gr.Column():
                gr.Markdown("### Detection Parameters")

                default_conf = gr.Slider(
                    minimum=0.1,
                    maximum=0.9,
                    value=0.25,
                    step=0.05,
                    label="Default Confidence Threshold"
                )

                iou_threshold = gr.Slider(
                    minimum=0.1,
                    maximum=0.9,
                    value=0.45,
                    step=0.05,
                    label="IOU Threshold",
                    info="Intersection over Union threshold for NMS"
                )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Chemical Analysis Settings")

                pixel_to_micron = gr.Number(
                    label="Pixel to Micron Conversion",
                    value=0.9785,
                    info="Fallback value if ND2 metadata unavailable"
                )

            with gr.Column():
                gr.Markdown("### Color Detection Ranges")

                lignin_sensitivity = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=5,
                    step=1,
                    label="Lignin Detection Sensitivity",
                    info="1=Very Strict, 10=Very Permissive"
                )

                pectin_sensitivity = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=5,
                    step=1,
                    label="Pectin Detection Sensitivity",
                    info="1=Very Strict, 10=Very Permissive"
                )

        # Save settings button
        save_settings_btn = gr.Button("💾 Save Settings", variant="primary")
        settings_status = gr.Textbox(label="Settings Status", interactive=False, lines=2)

        # Wire up settings
        check_model_btn.click(
            fn=segmentation_engine.check_model_status,
            inputs=[model_path],
            outputs=[model_status]
        )

        save_settings_btn.click(
            fn=config.save_settings,
            inputs=[model_path, default_conf, iou_threshold, pixel_to_micron,
                   lignin_sensitivity, pectin_sensitivity],
            outputs=[settings_status]
        )


def create_app():
    """Create and configure the Gradio app"""

    with gr.Blocks(
        title="Alfalfa Cell Segmentation Analysis",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {font-family: 'Arial', sans-serif;}
        h1 {color: #2c5530; text-align: center;}
        h2 {color: #3d7a3f;}
        """
    ) as app:

        # Header
        gr.Markdown("""
        # 🌱 Alfalfa Cell Segmentation Analysis Platform

        **AI-Powered Microscopy Analysis for Biologists**

        This platform analyzes alfalfa stem cross-sections using deep learning to detect cells
        and measure chemical composition (lignin and pectin). No coding required!

        ---
        """)

        # Create tabs
        upload_outputs = create_upload_tab()
        seg_outputs = create_segmentation_tab()
        chem_outputs = create_chemical_analysis_tab()
        results_outputs = create_results_tab()
        create_settings_tab()

        # Footer
        gr.Markdown("""
        ---

        **Developed for USDA Agricultural Research Service**

        *Questions? Contact your research coordinator or see the documentation.*
        """)

    return app


if __name__ == "__main__":
    # Create and launch app
    app = create_app()

    # Launch with sharing enabled for remote access
    app.launch(
        server_name="0.0.0.0",  # Allow external connections
        server_port=7860,
        share=False,  # Set to True to create public Gradio link
        show_error=True,
        quiet=False
    )
