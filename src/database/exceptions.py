"""
Custom exceptions for database operations.

This module defines custom exception classes for different types of database errors
that can occur in the application, providing more specific error handling
and better error messages.
"""

from typing import Optional, Any
from sqlalchemy.exc import SQLAlchemyError


class DatabaseError(Exception):
    """Base exception class for database-related errors."""
    
    def __init__(
        self, 
        message: str, 
        original_exception: Optional[Exception] = None,
        context: Optional[dict] = None
    ):
        """
        Initialize the DatabaseError.
        
        Args:
            message: Error message
            original_exception: The original exception that caused this error
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception
        self.context = context or {}


class DatabaseConnectionError(DatabaseError):
    """Exception for database connection errors."""
    pass


class DatabaseQueryError(DatabaseError):
    """Exception for database query errors."""
    pass


class DatabaseTransactionError(DatabaseError):
    """Exception for database transaction errors."""
    pass


class DatabaseConstraintError(DatabaseError):
    """Exception for database constraint violation errors."""
    pass


def create_database_error_from_sqlalchemy_error(
    sql_error: SQLAlchemyError, 
    context: Optional[dict] = None
) -> DatabaseError:
    """
    Create an appropriate DatabaseError from an SQLAlchemy error.
    
    Args:
        sql_error: SQLAlchemy error
        context: Additional context information
        
    Returns:
        Appropriate DatabaseError subclass
    """
    context = context or {}
    
    # Handle specific SQLAlchemy error types
    if "connection" in str(sql_error).lower():
        return DatabaseConnectionError(
            f"Database connection error: {sql_error}",
            original_exception=sql_error,
            context=context
        )
    elif "constraint" in str(sql_error).lower():
        return DatabaseConstraintError(
            f"Database constraint violation: {sql_error}",
            original_exception=sql_error,
            context=context
        )
    elif "transaction" in str(sql_error).lower():
        return DatabaseTransactionError(
            f"Database transaction error: {sql_error}",
            original_exception=sql_error,
            context=context
        )
    else:
        return DatabaseQueryError(
            f"Database query error: {sql_error}",
            original_exception=sql_error,
            context=context
        )