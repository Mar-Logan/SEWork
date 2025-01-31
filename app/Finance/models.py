from django.db import models

class Department(models.Model):

    
    DepartmentId = models.AutoField(primary_key=True, unique=True)# Unique identifier for the department
    DepartmentName = models.CharField(max_length=200) # Name of the department

    ManagerId = models.OneToOneField(# Manager assigned to the department
        "HR.Staff", on_delete=models.SET_NULL, null=True, blank=True, related_name="department"
    )
    # Department budget
    Budget = models.IntegerField()

    def __str__(self):# Returns the department name, and manager name if available
        if self.ManagerId:
            return f"{self.DepartmentName} - Manager: {self.ManagerId.StaffName}"
        return f"{self.DepartmentName}"

    def GetDepartmentStaff(self):
        # Retrieevs all staff members associated with the department assumes the 'staff' related_name is set on the ForeignKey in the Staff model.
        return self.staff.all()

    def GetDepartmentBudget(self):
        # Returns the current budget of the department
        return self.Budget

    def SetDepartmentBudget(self, budget):
        # Sets a new budget for the department if valid
        if isinstance(budget, int) and budget >= 0:
            self.Budget = budget
            self.save()
        else:
            raise ValueError("Budget must be a non-negative integer.")

    
