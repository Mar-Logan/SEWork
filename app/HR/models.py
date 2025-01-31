from django.db import models
from Finance.models import Department
from django.db.models import Sum, Avg, Count
from datetime import datetime, timedelta

class Staff(models.Model):
    # Unique identifier for each staff member
    StaffId = models.AutoField(primary_key=True, unique=True)

     # Name of the staff member
    StaffName = models.CharField(max_length=200)

    # Role of the staff member
    Role = models.CharField(max_length=200)

    # Salary of the staff member
    Salary = models.IntegerField()

    # Foreign key to the Department model
    DepartmentId = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff'  # Ensure related_name is added
    )
     # The hire date of the staff member
    #StartingDate = models.DateField(auto_now_add=True)

    def __str__(self):
      # Staff name, role, and department name (if available)
        if self.DepartmentId:
            return f"{self.StaffName} - Role: {self.Role} - In: {self.DepartmentId.DepartmentName}"
        return f"{self.StaffName} - Role: {self.Role}"

    def GetStaffData(self):
        # Retrieves the staff member's details as a dictionary.
        return {
            "StaffId": self.StaffId,
            "StaffName": self.StaffName,
            "Role": self.Role,
            "Salary": self.Salary,
            "Department": self.DepartmentId.DepartmentName if self.DepartmentId else None,
            "StartingDate": self.StartingDate,
        }

    def EditStaffData(self, **kwargs):
        """
        Edits the staff member's data.
        
        Args:
            kwargs (dict): Dictionary with keys 'StaffName', 'Role', 'Salary' and their new values.

        Raises:
            ValueError: If an invalid field is provided or if salary is invalid.
        """

        valid_fields = {'StaffName', 'Role', 'Salary'} # Define valid fields for update

        update_data = {k: v for k, v in kwargs.items() if k in valid_fields}# Filter out invalid fields from kwargs
        if not update_data:
            raise ValueError("No valid fields provided for update")

        # Validate Salary if being updated
        if 'Salary' in update_data:
            if not (isinstance(update_data['Salary'], int) and update_data['Salary'] >= 0):
                raise ValueError("Salary must be a non-negative integer.")

        # Update the fields with new values
        for field, value in update_data.items():
            setattr(self, field, value)
        self.full_clean()  # Validate all fields
        self.save()


    def AssignDepartment(self, DepartmentId):
       
        if isinstance(DepartmentId, Department): # Assigns the staff member to a department
            self.DepartmentId = DepartmentId   # The department instance to assign to the staff member
            self.save()
        else:
            raise ValueError("Invalid department instance.")



    def GetPerformanceData(self, date_range=30):
        """
        Analyses the staff member's performance based on sales over a given period.

        Args:
            date_range (int): Number of days to analyse

        Result:
            Performance metrics including total sales, average daily sales, and performance index.
        
        Raises:
            ValueError: If an error occurs during the calculation.
        """
        try:
            # Define the date range for the analysi
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range)

            
            sales_data = Staff.sales.filter(# Aggregate sales data for the staff member within the date range
                StaffId=self.StaffId,
                SalesDate__range=[start_date, end_date]
            ).aggregate(
                
                total_sales=Sum('total_amount'),
                average_daily_sales=Avg('total_amount'),
                total_transactions=Count('id'),
            )

            # Calculate additional metrics
            performance_metrics = {
                "staff_name": self.StaffName,
                "period_total_sales": sales_data["total_sales"] or 0,
                "average_daily_sales": sales_data["average_daily_sales"] or 0,
                
                "total_transactions": sales_data["total_transactions"] or 0,
                "sales_per_day": (sales_data["total_sales"] or 0) / date_range,
                "performance_index": (sales_data["total_sales"] or 0) / (self.Salary or 1),  # Normalise by salary
            }

            return performance_metrics

        except Exception as e:
            raise ValueError(f"Error calculating staff performance: {str(e)}")
