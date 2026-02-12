from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Optional, Tuple

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class Validator:
    """Utility class for input validation."""
    
    @staticmethod
    def validate_symbol(symbol: str) -> Tuple[bool, Optional[str]]:
        """
        Validate instrument symbol.
        
        Args:
            symbol: Symbol to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not symbol or not isinstance(symbol, str):
            return False, "El símbolo es requerido"
        
        symbol = symbol.strip()
        
        if len(symbol) < 1 or len(symbol) > 20:
            return False, "El símbolo debe tener entre 1 y 20 caracteres"
        
        # Allow alphanumeric and hyphens
        if not all(c.isalnum() or c in ['-', '.'] for c in symbol):
            return False, "El símbolo contiene caracteres inválidos"
        
        return True, None
    
    @staticmethod
    def validate_instrument_type(instrument_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate instrument type.
        
        Args:
            instrument_type: Type to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        valid_types = ['stock', 'etf', 'crypto']
        
        if not instrument_type:
            return False, "El tipo de instrumento es requerido"
        
        if instrument_type.lower() not in valid_types:
            return False, f"Tipo inválido. Debe ser: {', '.join(valid_types)}"
        
        return True, None
    
    @staticmethod
    def validate_quantity(quantity: str, allow_zero: bool = False) -> Tuple[bool, Optional[str], Optional[Decimal]]:
        """
        Validate quantity value.
        
        Args:
            quantity: Quantity as string
            allow_zero: Whether to allow zero values
            
        Returns:
            tuple: (is_valid, error_message, decimal_value)
        """
        if not quantity:
            return False, "La cantidad es requerida", None
        
        try:
            dec_quantity = Decimal(str(quantity))
            
            if dec_quantity < 0:
                return False, "La cantidad no puede ser negativa", None
            
            if not allow_zero and dec_quantity == 0:
                return False, "La cantidad debe ser mayor que cero", None
            
            # Check decimal places (max 12)
            if dec_quantity.as_tuple().exponent < -12:
                return False, "La cantidad no puede tener más de 12 decimales", None
            
            return True, None, dec_quantity
            
        except (InvalidOperation, ValueError):
            return False, "Cantidad inválida", None
    
    @staticmethod
    def validate_price(price: str) -> Tuple[bool, Optional[str], Optional[Decimal]]:
        """
        Validate price value.
        
        Args:
            price: Price as string
            
        Returns:
            tuple: (is_valid, error_message, decimal_value)
        """
        if not price:
            return False, "El precio es requerido", None
        
        try:
            dec_price = Decimal(str(price))
            
            if dec_price <= 0:
                return False, "El precio debe ser mayor que cero", None
            
            # Check decimal places (max 8)
            if dec_price.as_tuple().exponent < -8:
                return False, "El precio no puede tener más de 8 decimales", None
            
            return True, None, dec_price
            
        except (InvalidOperation, ValueError):
            return False, "Precio inválido", None
    
    @staticmethod
    def validate_commission(commission: str) -> Tuple[bool, Optional[str], Optional[Decimal]]:
        """
        Validate commission value.
        
        Args:
            commission: Commission as string
            
        Returns:
            tuple: (is_valid, error_message, decimal_value)
        """
        if not commission:
            return False, "La comisión es requerida", None
        
        try:
            dec_commission = Decimal(str(commission))
            
            if dec_commission < 0:
                return False, "La comisión no puede ser negativa", None
            
            # Check decimal places (max 2)
            if dec_commission.as_tuple().exponent < -2:
                return False, "La comisión no puede tener más de 2 decimales", None
            
            return True, None, dec_commission
            
        except (InvalidOperation, ValueError):
            return False, "Comisión inválida", None
    
    @staticmethod
    def validate_date(date_str: str) -> Tuple[bool, Optional[str], Optional[datetime]]:
        """
        Validate date string.
        
        Args:
            date_str: Date as string (YYYY-MM-DD)
            
        Returns:
            tuple: (is_valid, error_message, datetime_value)
        """
        if not date_str:
            return False, "La fecha es requerida", None
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Check if date is not in the future
            if date_obj.date() > datetime.now().date():
                return False, "La fecha no puede estar en el futuro", None
            
            return True, None, date_obj
            
        except ValueError:
            return False, "Formato de fecha inválido (use YYYY-MM-DD)", None
    
    @staticmethod
    def validate_transaction_type(transaction_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate transaction type.
        
        Args:
            transaction_type: Type to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        valid_types = ['buy', 'sell']
        
        if not transaction_type:
            return False, "El tipo de transacción es requerido"
        
        if transaction_type.lower() not in valid_types:
            return False, f"Tipo inválido. Debe ser: {', '.join(valid_types)}"
        
        return True, None