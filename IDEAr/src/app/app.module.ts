import { NgModule } from '@angular/core';
import {
  BrowserModule,
  provideClientHydration,
} from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ItemDescriptionComponent } from './item-description/item-description.component';
import { ItemComponent } from './item/item.component';
import { ItemSearchComponent } from './item-search/item-search.component';
import { ReactiveFormsModule } from '@angular/forms';
import { HomeComponent } from './home/home.component';
import { AdminComponent } from './admin/admin.component';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: '', component: AppComponent }, // Home Page
  { path: 'admin', component: AdminComponent }, // Admin Page
];

@NgModule({
  declarations: [
    AppComponent,
    ItemDescriptionComponent,
    ItemComponent,
    ItemSearchComponent,
    HomeComponent,
    AdminComponent,
  ],
  imports: [
    ReactiveFormsModule,
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    RouterModule.forRoot(routes),
  ],
  exports: [RouterModule],
  providers: [provideClientHydration()],
  bootstrap: [AppComponent],
})
export class AppModule {}
