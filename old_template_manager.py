import jinja2
from pathlib import Path
from typing import Dict, Any

class TemplateManager:
    """
    Handles loading Jinja2 templates and rendering them into input files.
    """
    def __init__(self, template_dir: Path):
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            undefined=jinja2.StrictUndefined # Fail error if a variable is missing!
        )

    def render_and_write(self, template_name: str, output_path: Path, context: Dict[str, Any]):
        """
        template_name: e.g., 'orca_opt.inp.j2'
        output_path: Where to save the finished file
        context: A dictionary of variables to fill into the template
        """
        try:
            template = self.template_env.get_template(template_name)
            rendered_content = template.render(context)
            
            # Write to file
            with open(output_path, 'w') as f:
                f.write(rendered_content)
                
            print(f"Generated input: {output_path}")
            
        except jinja2.TemplateError as e:
            print(f"Error rendering template {template_name}: {e}")
            raise # Stop everything if generation fails