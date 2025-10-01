"""Web interface using Gradio."""

import gradio as gr
from typing import Optional, Tuple, List
import json

from .rag_pipeline import RAGPipeline


class WebInterface:
    """Gradio web interface for the RAG system."""
    
    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag_pipeline = rag_pipeline
        self.interface = None
        
    def create_interface(self):
        """Create the Gradio interface."""
        with gr.Blocks(title="RAG Agriculture System", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🌾 ระบบถามตอบข้อมูลเกษตร (RAG Agriculture System)")
            gr.Markdown("ถามคำถามเกี่ยวกับเนื้อหาเกษตรกรรม และรับคำตอบที่มาจากฐานข้อมูลที่น่าเชื่อถือ")
            
            with gr.Tab("💬 ถาม-ตอบ"):
                self._create_qa_tab()
            
            with gr.Tab("🔍 ค้นหาเอกสาร"):
                self._create_search_tab()
            
            with gr.Tab("📊 ข้อมูลระบบ"):
                self._create_system_info_tab()
        
        self.interface = interface
        return interface
    
    def _create_qa_tab(self):
        """Create the Q&A tab."""
        with gr.Row():
            with gr.Column(scale=3):
                question_input = gr.Textbox(
                    lines=2,
                    placeholder="พิมพ์คำถามของคุณที่นี่ (ไทย/อังกฤษได้)",
                    label="คำถาม"
                )
                
                with gr.Row():
                    submit_btn = gr.Button("ถาม", variant="primary")
                    clear_btn = gr.Button("ล้าง", variant="secondary")
                
                debug_checkbox = gr.Checkbox(
                    label="แสดงข้อมูลการค้นหา (Debug)",
                    value=False
                )
            
            with gr.Column(scale=4):
                answer_output = gr.Textbox(
                    lines=10,
                    label="คำตอบ",
                    interactive=False
                )
        
        # Event handlers
        submit_btn.click(
            fn=self._process_question,
            inputs=[question_input, debug_checkbox],
            outputs=answer_output
        )
        
        clear_btn.click(
            fn=lambda: ("", ""),
            outputs=[question_input, answer_output]
        )
        
        question_input.submit(
            fn=self._process_question,
            inputs=[question_input, debug_checkbox],
            outputs=answer_output
        )
    
    def _create_search_tab(self):
        """Create the document search tab."""
        with gr.Row():
            with gr.Column(scale=2):
                search_input = gr.Textbox(
                    lines=1,
                    placeholder="ค้นหาเอกสารที่เกี่ยวข้อง",
                    label="คำค้นหา"
                )
                
                num_results = gr.Slider(
                    minimum=1,
                    maximum=20,
                    value=5,
                    step=1,
                    label="จำนวนผลลัพธ์"
                )
                
                search_btn = gr.Button("ค้นหา", variant="primary")
            
            with gr.Column(scale=3):
                search_results = gr.JSON(
                    label="ผลการค้นหา",
                    show_label=True
                )
        
        search_btn.click(
            fn=self._search_documents,
            inputs=[search_input, num_results],
            outputs=search_results
        )
    
    def _create_system_info_tab(self):
        """Create the system information tab."""
        with gr.Column():
            gr.Markdown("## ข้อมูลระบบ")
            
            refresh_btn = gr.Button("รีเฟรชข้อมูล", variant="secondary")
            
            system_info = gr.JSON(
                label="ข้อมูลฐานข้อมูล",
                value=self._get_system_info()
            )
            
            refresh_btn.click(
                fn=self._get_system_info,
                outputs=system_info
            )
    
    def _process_question(self, question: str, debug: bool = False) -> str:
        """Process a question through the RAG pipeline."""
        if not question.strip():
            return "กรุณาใส่คำถาม"
        
        try:
            return self.rag_pipeline.query(question, debug=debug)
        except Exception as e:
            return f"เกิดข้อผิดพลาด: {e}"
    
    def _search_documents(self, query: str, num_results: int) -> List[dict]:
        """Search for similar documents."""
        if not query.strip():
            return []
        
        try:
            return self.rag_pipeline.get_similar_documents(query, k=num_results)
        except Exception as e:
            return [{"error": f"เกิดข้อผิดพลาดในการค้นหา: {e}"}]
    
    def _get_system_info(self) -> dict:
        """Get system information."""
        try:
            return self.rag_pipeline.vector_store_manager.get_collection_info()
        except Exception as e:
            return {"error": f"ไม่สามารถดึงข้อมูลระบบได้: {e}"}
    
    def launch(self, share: bool = False, server_name: str = "127.0.0.1", server_port: int = 7860):
        """Launch the Gradio interface."""
        if not self.interface:
            self.create_interface()
        
        print(f"🚀 Starting web interface at http://{server_name}:{server_port}")
        
        return self.interface.launch(
            share=share,
            server_name=server_name,
            server_port=server_port,
            show_error=True
        )


def create_simple_interface(rag_pipeline: RAGPipeline) -> gr.Interface:
    """Create a simple Gradio interface for backward compatibility."""
    def process_question(question: str) -> str:
        if not question.strip():
            return "กรุณาใส่คำถาม"
        return rag_pipeline.query(question)
    
    return gr.Interface(
        fn=process_question,
        inputs=gr.Textbox(
            lines=2,
            placeholder="พิมพ์คำถามของคุณที่นี่ (ไทย/อังกฤษได้)"
        ),
        outputs="text",
        title="ถามข้อมูลเกี่ยวกับ Agro (RAG)",
        description="ถามคำถามเกี่ยวกับเนื้อหา แล้วรับคำตอบสรุปเป็นข้อเท็จจริงสำคัญ (ตอบเป็นไทย)",
    )
