import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';   // Home Page Component
import { AdminComponent } from './admin/admin.component'; // Admin Page Component

const routes: Routes = [
  { path: '', component: HomeComponent }, // Home Page
  { path: 'admin', component: AdminComponent }, // Admin Page
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
