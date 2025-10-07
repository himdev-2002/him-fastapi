from pydantic import BaseModel, ValidationError
from typing import Dict, Any, Optional

class I18nErrorFormatter:
    # Translations dictionary
    TRANSLATIONS = {
        "en": {
            "missing": "This field is required",

            # Type errors
            "type_error.integer": "Please enter a valid number",
            "type_error.float": "Please enter a valid decimal number",
            "type_error.bool": "Please enter a valid yes/no value",
            "type_error.str": "Please enter a text value",
            "type_error.list": "Please enter a list of values",
            "type_error.dict": "Please enter valid data",
            
            # Value errors
            "value_error.email": "Please enter a valid email address",
            "value_error.url": "Please enter a valid URL",
            "value_error.date": "Please enter a valid date (YYYY-MM-DD)",
            "value_error.time": "Please enter a valid time (HH:MM:SS)",
            "value_error.datetime": "Please enter a valid date and time",
            "value_error.missing": "This field is required",
            
            # String errors
            "value_error.any_str.min_length": "This field must be at least {limit_value} characters",
            "value_error.any_str.max_length": "This field cannot exceed {limit_value} characters",
            
            # Number errors
            "value_error.number.not_ge": "This value must be at least {limit_value}",
            "value_error.number.not_le": "This value cannot exceed {limit_value}",
            "value_error.number.not_gt": "This value must be greater than {limit_value}",
            "value_error.number.not_lt": "This value must be less than {limit_value}",
            
            # Enum errors
            "type_error.enum": "Please select a valid option"
            # More English translations...
        },
        "es": {
            "missing": "Este campo es obligatorio",
            
            # Type errors
            "type_error.integer": "Por favor ingrese un número válido",
            "type_error.float": "Por favor ingrese un número decimal válido",
            "type_error.bool": "Por favor ingrese un valor válido (si/no)",
            "type_error.str": "Por favor ingrese un texto válido",
            "type_error.list": "Por favor ingrese una lista de valores válidos",
            "type_error.dict": "Por favor ingrese datos válidos",
            
            # Value errors
            "value_error.email": "Por favor ingrese un correo electrónico válido",
            "value_error.url": "Por favor ingrese una URL válida",
            "value_error.date": "Por favor ingrese una fecha válida (YYYY-MM-DD)",
            "value_error.time": "Por favor ingrese una hora válida (HH:MM:SS)",
            "value_error.datetime": "Por favor ingrese una fecha y hora válidas",
            "value_error.missing": "Este campo es obligatorio",
            
            # String errors
            "value_error.any_str.min_length": "Este campo debe tener al menos {limit_value} caracteres",
            "value_error.any_str.max_length": "Este campo no puede exceder {limit_value} caracteres",
            
            # Number errors
            "value_error.number.not_ge": "Este valor debe ser al menos {limit_value}",
            "value_error.number.not_le": "Este valor no puede exceder {limit_value}",
            "value_error.number.not_gt": "Este valor debe ser mayor que {limit_value}",
            "value_error.number.not_lt": "Este valor debe ser menor que {limit_value}",
            
            # Enum errors
            "type_error.enum": "Por favor seleccione una opción válida"
            # More Spanish translations...
        },
        "fr": {
            "missing": "Ce champ est obligatoire",
            
            # Type errors
            "type_error.integer": "Veuillez saisir un nombre valide",
            "type_error.float": "Veuillez saisir un nombre décimal valide",
            "type_error.bool": "Veuillez saisir une valeur valide (oui/non)",
            "type_error.str": "Veuillez saisir un texte valide",
            "type_error.list": "Veuillez saisir une liste de valeurs valides",
            "type_error.dict": "Veuillez saisir des données valides",
            
            # Value errors
            "value_error.email": "Veuillez saisir une adresse e-mail valide",
            "value_error.url": "Veuillez saisir une URL valide",
            "value_error.date": "Veuillez saisir une date valide (YYYY-MM-DD)",
            "value_error.time": "Veuillez saisir une heure valide (HH:MM:SS)",
            "value_error.datetime": "Veuillez saisir une date et heure valides",
            "value_error.missing": "Ce champ est obligatoire",
            
            # String errors
            "value_error.any_str.min_length": "Ce champ doit avoir au moins {limit_value} caractères",
            "value_error.any_str.max_length": "Ce champ ne peut pas dépasser {limit_value} caractères",
            
            # Number errors
            "value_error.number.not_ge": "Cette valeur doit être au moins {limit_value}",
            "value_error.number.not_le": "Cette valeur ne peut pas dépasser {limit_value}",
            "value_error.number.not_gt": "Cette valeur doit être supérieure à {limit_value}",
            "value_error.number.not_lt": "Cette valeur doit être inférieure à {limit_value}",
            
            # Enum errors
            "type_error.enum": "Veuillez sélectionner une option valide"
            # More French translations...
        }
    }
    
    @classmethod
    def translate_error(cls, error_type: str, error_msg: str, 
                       language: str = "en", 
                       ctx: Optional[Dict[str, Any]] = None) -> str:
        """Translate an error message to the specified language"""
        if language not in cls.TRANSLATIONS:
            language = "en"  # Fallback to English
            
        translations = cls.TRANSLATIONS[language]
        template = translations.get(error_type, error_msg)
        
        # Replace placeholders with context values
        if ctx:
            for key, value in ctx.items():
                placeholder = "{" + key + "}"
                if placeholder in template:
                    template = template.replace(placeholder, str(value))
                    
        return template

    @classmethod
    def format_errors(cls, error: ValidationError, language: str = "en") -> Dict[str, Any]:
        """Format all validation errors with translations"""
        result: Dict[str, Any] = {}
        
        for err in error.errors():
            loc = err["loc"]
            field_name = loc[-1] if loc else ""
            
            if isinstance(field_name, int):
                field_name = loc[-2] if len(loc) > 1 else "item"
                field_name = f"{field_name}[{loc[-1]}]"
            
            error_type = err.get("type", "")
            error_msg = err.get("msg", "")
            error_ctx = err.get("ctx")
            
            translated_msg = cls.translate_error(
                error_type, error_msg, language, error_ctx
            )
            
            if field_name not in result:
                result[field_name] = []
                
            result[field_name].append(translated_msg)
            
        return result

# Usage example
# class User(BaseModel):
#     name: str
#     email: str
#     age: int

# try:
#     user = User(name="", email="not-an-email", age="thirty")
# except ValidationError as e:
#     # English errors
#     en_errors = I18nErrorFormatter.format_errors(e, "en")
#     print("English errors:", en_errors)
    
#     # Spanish errors
#     es_errors = I18nErrorFormatter.format_errors(e, "es")
#     print("Spanish errors:", es_errors)
